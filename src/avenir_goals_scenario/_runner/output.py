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

#: Column name holding the scenario identifier in the long-format output. It is
#: written as a data column rather than a partition directory, so many scenarios
#: can share one Parquet file while remaining efficiently filterable via
#: row-group statistics.
SCENARIO_ID_COLUMN = "scenario_id"


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


def write_scenario_batch(
    output_dir: Path,
    pjnz_name: str,
    part_name: str,
    batch: list[tuple[str, list[dict[str, np.ndarray]]]],
    indicator_dims: IndicatorDims,
) -> None:
    """Write one batch of scenarios as a single Parquet file per indicator.

    All scenarios in the batch share one file per indicator::

        {output_dir}/{indicator}/pjnz_name={pjnz_name}/{part_name}.parquet

    Each scenario's simulations become long-format rows carrying a constant
    ``scenario_id`` data column; the batch is concatenated and written in a
    single :func:`pyarrow.parquet.write_table` call, so pyarrow sizes the row
    groups itself (good compression) and the file is produced in one open →
    write → close. Peak memory is one batch in flight.

    If writing any indicator raises, every file written for this batch is deleted
    before re-raising, so a failed batch leaves no partial output behind and the
    caller can re-run it with ``--retry``.

    Does **not** write ``_metadata``; call :func:`consolidate_metadata` once from
    a single process after all batches have been written.

    Args:
        output_dir: Root directory of the partitioned dataset.
        pjnz_name: Stem of the source PJNZ file (the ``pjnz_name=`` partition).
        part_name: Base file name for this batch (e.g. ``"part-0"``).
        batch: List of ``(scenario_id, sim_output)`` pairs. Each ``sim_output``
            is a list of per-simulation dicts sharing the same indicator keys.
        indicator_dims: Mapping of indicator name to dimension specs.

    Raises:
        UnknownIndicatorError: If a produced indicator has no dimension specs.
    """
    if not batch:
        return

    # Validate up front so an unknown indicator fails before anything is written.
    indicators = list(batch[0][1][0])
    specs = {}
    for indicator in indicators:
        raw_specs = indicator_dims.get(indicator)
        if raw_specs is None:
            raise UnknownIndicatorError(indicator, list(indicator_dims.keys()))
        specs[indicator] = raw_specs

    written: list[Path] = []
    try:
        for indicator in indicators:
            tables = [
                _to_long_table([sim[indicator] for sim in sim_output], specs[indicator], scenario_id=scenario_id)
                for scenario_id, sim_output in batch
            ]
            path = output_dir / f"{indicator}" / f"pjnz_name={pjnz_name}" / f"{part_name}.parquet"
            path.parent.mkdir(parents=True, exist_ok=True)
            pq.write_table(pa.concat_tables(tables), path)
            written.append(path)
    except Exception:
        # Discard any partial output so consolidate_metadata stays consistent and
        # the whole batch can be regenerated on --retry.
        for path in written:
            path.unlink(missing_ok=True)
        raise

    logger.debug("Wrote batch {} ({} scenario(s)) for pjnz={}", part_name, len(batch), pjnz_name)


def consolidate_metadata(output_dir: Path) -> None:
    """Write a ``_metadata`` file per indicator directory.

    Aggregates row-group statistics (min/max per column, row counts) from every
    parquet file within each indicator subdirectory so that query engines can do
    predicate pushdown without opening individual files.

    Each indicator gets its own ``_metadata`` because indicators have different
    schemas - a single root-level ``_metadata`` is not written.

    Must be called from a **single process** after all
    :func:`write_scenario_batch` calls have completed.

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
            try:
                combined.append_row_groups(pq.read_metadata(path))
            except Exception as exc:
                err_msg = (
                    f"Schema mismatch in {indicator_dir.name}: cannot combine "
                    f"{path.relative_to(indicator_dir)} with earlier files. "
                    "This usually means output from different versions of goals-scenario "
                    f"is mixed in {indicator_dir}. Delete that directory and re-run to resolve."
                )
                raise ValueError(err_msg) from exc
        combined.write_metadata_file(str(indicator_dir / "_metadata"))
        logger.debug("Written _metadata under {}", indicator_dir)


def _coerce_spec(dim: str | DimSpec) -> DimSpec:
    return dim if isinstance(dim, DimSpec) else DimSpec(name=dim)


def _dim_field(spec: DimSpec) -> pa.Field:
    if spec.labels is not None:
        return pa.field(spec.name, pa.dictionary(pa.int8(), pa.utf8()))
    return pa.field(spec.name, pa.int16())


def _indicator_schema(specs: tuple[DimSpec, ...], *, with_scenario_id: bool = False) -> pa.Schema:
    scenario_field = [pa.field(SCENARIO_ID_COLUMN, pa.utf8())] if with_scenario_id else []
    return pa.schema([
        *scenario_field,
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
    scenario_id: str | None = None,
) -> pa.Table:
    """Convert a list of per-simulation F-contiguous arrays to a long-format Arrow table.

    Output columns are ``[scenario_id,] <dim columns…>, simulation, value`` where
    the first dimension (e.g. age) varies fastest across rows.

    Args:
        arrays: One array per simulation, all with the same shape.  Arrays are
            expected to be F-contiguous float64.
        specs: One `DimSpec` (or plain string) per array dimension. A plain
            string is shorthand for ``DimSpec(name=string)``.
        scenario_id: If given, a leading ``scenario_id`` column holding this
            (constant) value is added. Kept constant per table so that each
            appended row group carries tight ``scenario_id`` statistics.

    Raises:
        DimNamesMismatchError: If ``len(specs) != arrays[0].ndim``.
    """
    n_sims = len(arrays)
    shape = arrays[0].shape
    n_per_sim = int(np.prod(shape))

    if len(specs) != len(shape):
        raise DimNamesMismatchError(len(specs), len(shape))

    specs = tuple(_coerce_spec(s) for s in specs)
    schema = _indicator_schema(specs, with_scenario_id=scenario_id is not None)

    # F-order ravel is zero-copy for F-contiguous leapfrog arrays.
    values = np.concatenate([arr.ravel(order="F") for arr in arrays])

    sim_col = pa.array(
        np.repeat(np.arange(n_sims, dtype=np.int32), n_per_sim),
        type=pa.int32(),
    )

    columns: dict[str, pa.Array] = {}
    if scenario_id is not None:
        columns[SCENARIO_ID_COLUMN] = pa.array([str(scenario_id)] * (n_sims * n_per_sim), type=pa.utf8())
    columns.update(_build_index_columns(shape, n_sims, specs))
    columns["simulation"] = sim_col
    columns["value"] = pa.array(values, type=pa.float64())

    return pa.table(columns, schema=schema)
