from collections.abc import Sequence
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
from loguru import logger

from avenir_goals_scenario._runner.indicator_dims import (
    DimNamesMismatchError,
    DimSpec,
    IndicatorDims,
    UnknownIndicatorError,
)


def check_indicator_dims(
    output_indicators: list[str],
    indicator_dims: IndicatorDims,
) -> None:
    """Raise :class:`UnknownIndicatorError` for any indicator that lacks dimension specs.

    Call this before starting simulations so the error surfaces immediately
    rather than after potentially expensive computation.

    Args:
        output_indicators: Indicator names that will be written.
        indicator_dims: Mapping of indicator name to dimension specs.

    Raises:
        UnknownIndicatorError: If any indicator in ``output_indicators`` is
            absent from ``indicator_dims``.
    """
    supported = list(indicator_dims.keys())
    for indicator in output_indicators:
        if indicator not in indicator_dims:
            raise UnknownIndicatorError(indicator, supported)


def write_scenario_results(
    scenario_id: int,
    pjnz_name: str,
    sim_output: list[dict[str, np.ndarray]],
    output_dir: Path,
    indicator_dims: IndicatorDims | None = None,
) -> None:
    """Write simulation results for one scenario/PJNZ as a partitioned Parquet dataset.

    Writes one parquet file per indicator under::

        {output_dir}/{indicator}/pjnz_name={pjnz_name}/scenario_id={scenario_id}/part-0.parquet

    Each file is in long format with columns ``<dim columns…>, simulation, value``.
    Dimension column names and encodings are taken from ``indicator_dims``.
    Every indicator present in ``sim_output`` must have an entry in
    ``indicator_dims``; a missing entry raises :class:`UnknownIndicatorError`.
    Different indicators may have entirely different schemas.

    This function is safe to call from multiple processes concurrently provided
    each call uses a distinct (indicator, pjnz_name, scenario_id) combination.
    It deliberately does **not** write ``_metadata`` or ``_common_metadata``.
    Call :func:`consolidate_metadata` once from a single process after all
    workers have finished.

    Args:
        scenario_id: Scenario identifier used in the partition path.
        pjnz_name: Stem of the source PJNZ file (e.g. ``"country_2024"``).
        sim_output: List of dicts of simulation output.  Each list item is one
            simulation; every dict contains the same indicator keys.
        output_dir: Root directory for the partitioned dataset.
        indicator_dims: Optional mapping of indicator name to a tuple of
            :class:`DimSpec` (or plain strings as shorthand). Example::

                {
                    "p_hivpop": (
                        DimSpec("age"),
                        DimSpec("sex", labels=["male", "female"]),
                        DimSpec("year", offset=2010),
                    )
                }
    """
    indicator_dims = indicator_dims or {}
    out_indicators = sim_output[0].keys()

    for indicator in out_indicators:
        arrays = [sim[indicator] for sim in sim_output]

        raw_specs = indicator_dims.get(indicator)
        if raw_specs is None:
            raise UnknownIndicatorError(indicator, list(indicator_dims.keys()))
        table = _to_long_table(arrays, raw_specs)

        part_dir = output_dir / f"{indicator}" / f"pjnz_name={pjnz_name}" / f"scenario_id={scenario_id}"
        part_dir.mkdir(parents=True, exist_ok=True)
        pq.write_table(table, part_dir / "part-0.parquet")

        logger.debug(
            "Written indicator={} pjnz={} scenario={}",
            indicator,
            pjnz_name,
            scenario_id,
        )


def consolidate_metadata(output_dir: Path) -> None:
    """Write a ``_metadata`` file per indicator directory.

    Aggregates row-group statistics (min/max per column, row counts) from every
    parquet file within each indicator subdirectory so that query engines can do
    predicate pushdown without opening individual files.

    Each indicator gets its own ``_metadata`` because indicators have different
    schemas - a single root-level ``_metadata`` is not written.

    Must be called from a **single process** after all
    :func:`write_scenario_results` calls have completed.

    Args:
        output_dir: Root of the partitioned dataset.
    """
    indicator_dirs = [d for d in sorted(output_dir.iterdir()) if d.is_dir()]
    if not indicator_dirs:
        logger.warning("consolidate_metadata: no indicator directories found under {}", output_dir)
        return

    for indicator_dir in indicator_dirs:
        files = sorted(indicator_dir.rglob("*.parquet"))
        if not files:
            continue
        combined = pq.read_metadata(files[0])
        for path in files[1:]:
            combined.append_row_groups(pq.read_metadata(path))
        combined.write_metadata_file(str(indicator_dir / "_metadata"))
        logger.debug("Written _metadata under {}", indicator_dir)


def _coerce_spec(dim: str | DimSpec) -> DimSpec:
    return dim if isinstance(dim, DimSpec) else DimSpec(name=dim)


def _dim_field(spec: DimSpec) -> pa.Field:
    if spec.labels is not None:
        return pa.field(spec.name, pa.dictionary(pa.int8(), pa.utf8()))
    return pa.field(spec.name, pa.int16())


def _indicator_schema(specs: tuple[DimSpec, ...]) -> pa.Schema:
    return pa.schema([
        *[_dim_field(s) for s in specs],
        pa.field("simulation", pa.int32()),
        pa.field("value", pa.float64()),
    ])


def _build_index_columns(shape: tuple, n_sims: int, specs: tuple) -> dict:
    """Build dimension index columns for one sim's worth of elements, tiled n_sims times.

    Uses Fortran/column-major traversal so the first dimension varies fastest,
    matching the memory layout of F-contiguous leapfrog arrays.
    """
    base_indices = np.indices(shape, dtype=np.int16)
    return {
        spec.name: _build_dim_array(spec, np.tile(base_indices[i].ravel(order="F"), n_sims))
        for i, spec in enumerate(specs)
    }


def _build_dim_array(spec: DimSpec, flat_index: np.ndarray) -> pa.Array:
    if spec.labels is not None:
        return pa.DictionaryArray.from_arrays(
            pa.array(flat_index.astype(np.int8), type=pa.int8()),
            pa.array(spec.labels, type=pa.utf8()),
        )
    values = flat_index if spec.offset == 0 else (flat_index + spec.offset)
    return pa.array(values.astype(np.int16, copy=False), type=pa.int16())


def _to_long_table(
    arrays: list[np.ndarray],
    specs: Sequence[str | DimSpec],
) -> pa.Table:
    """Convert a list of per-simulation F-contiguous arrays to a long-format Arrow table.

    Output columns are ``<dim columns…>, simulation, value`` where the first
    dimension (e.g. age) varies fastest across rows.

    Args:
        arrays: One array per simulation, all with the same shape.  Arrays are
            expected to be F-contiguous float64.
        specs: One `DimSpec` (or plain string) per array dimension. A plain
            string is shorthand for ``DimSpec(name=string)``.

    Raises:
        DimNamesMismatchError: If ``len(specs) != arrays[0].ndim``.
    """
    n_sims = len(arrays)
    shape = arrays[0].shape
    n_per_sim = int(np.prod(shape))

    if len(specs) != len(shape):
        raise DimNamesMismatchError(len(specs), len(shape))

    specs = tuple(_coerce_spec(s) for s in specs)
    schema = _indicator_schema(specs)

    # F-order ravel is zero-copy for F-contiguous leapfrog arrays.
    values = np.concatenate([arr.ravel(order="F") for arr in arrays])

    sim_col = pa.array(
        np.repeat(np.arange(n_sims, dtype=np.int32), n_per_sim),
        type=pa.int32(),
    )

    columns: dict[str, pa.Array] = {}
    columns.update(_build_index_columns(shape, n_sims, specs))
    columns["simulation"] = sim_col
    columns["value"] = pa.array(values, type=pa.float64())

    return pa.table(columns, schema=schema)
