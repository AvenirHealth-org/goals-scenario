import contextlib
import shutil
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
#: written as a data column (constant per scenario, one row group per scenario)
#: rather than a partition directory, so many scenarios can share one Parquet
#: file while remaining efficiently filterable via row-group statistics.
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


class ScenarioChunkWriter:
    """Streams many scenarios' results into one Parquet file per indicator.

    All scenarios in one ``(PJNZ, chunk)`` work unit share a single file per
    indicator::

        {output_dir}/{indicator}/pjnz_name={pjnz_name}/{part_name}.parquet

    Each scenario is appended as **one row group** (containing all of its
    simulations) via a persistent :class:`pyarrow.parquet.ParquetWriter`, so
    peak memory is one scenario in flight regardless of how many scenarios the
    chunk holds, and only one file is created per indicator regardless of
    scenario count. ``scenario_id`` is written as a data column (constant within
    each row group), keeping per-scenario predicate pushdown precise.

    When ``staging_dir`` is given, files are written there first and copied to
    ``output_dir`` on :meth:`close`, so an object-store ``output_dir`` receives a
    single upload per file rather than per-row-group flushes. When it is
    ``None`` files are written directly under ``output_dir``.

    Does **not** write ``_metadata``; call :func:`consolidate_metadata` once from
    a single process after all writers have closed.
    """

    def __init__(
        self,
        output_dir: Path,
        pjnz_name: str,
        part_name: str,
        indicator_dims: IndicatorDims,
        staging_dir: Path | None = None,
    ) -> None:
        self._output_dir = output_dir
        self._pjnz_name = pjnz_name
        self._part_name = part_name
        self._indicator_dims = indicator_dims
        self._staging_dir = staging_dir
        # indicator -> (writer, staged_path, final_path)
        self._writers: dict[str, tuple[pq.ParquetWriter, Path, Path]] = {}

    def _partition_dir(self, root: Path, indicator: str) -> Path:
        return root / f"{indicator}" / f"pjnz_name={self._pjnz_name}"

    def _open_writer(self, indicator: str, schema: pa.Schema) -> pq.ParquetWriter:
        final_path = self._partition_dir(self._output_dir, indicator) / f"{self._part_name}.parquet"
        write_root = self._staging_dir if self._staging_dir is not None else self._output_dir
        staged_path = self._partition_dir(write_root, indicator) / f"{self._part_name}.parquet"
        staged_path.parent.mkdir(parents=True, exist_ok=True)
        writer = pq.ParquetWriter(staged_path, schema)
        self._writers[indicator] = (writer, staged_path, final_path)
        return writer

    def write_scenario(self, scenario_id: str, sim_output: list[dict[str, np.ndarray]]) -> None:
        """Append one scenario's simulations as a row group to each indicator file."""
        for indicator in sim_output[0]:
            arrays = [sim[indicator] for sim in sim_output]
            raw_specs = self._indicator_dims.get(indicator)
            if raw_specs is None:
                raise UnknownIndicatorError(indicator, list(self._indicator_dims.keys()))
            table = _to_long_table(arrays, raw_specs, scenario_id=scenario_id)

            existing = self._writers.get(indicator)
            writer = existing[0] if existing is not None else self._open_writer(indicator, table.schema)
            writer.write_table(table)

        logger.debug("Appended scenario={} pjnz={} to {}", scenario_id, self._pjnz_name, self._part_name)

    def close(self) -> None:
        """Finalise every file, copying from the staging dir if one is in use."""
        for writer, staged_path, final_path in self._writers.values():
            writer.close()
            if staged_path != final_path:
                final_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(staged_path), str(final_path))
        self._writers.clear()

    def abort(self) -> None:
        """Close writers and delete any part files for this unit (best effort).

        Used when a write fails mid-chunk: the file is potentially corrupt, so it
        is removed and every scenario in the chunk is re-run on ``--retry``.
        """
        for writer, staged_path, final_path in self._writers.values():
            with contextlib.suppress(Exception):  # already aborting; nothing useful to do
                writer.close()
            staged_path.unlink(missing_ok=True)
            final_path.unlink(missing_ok=True)
        self._writers.clear()


def consolidate_metadata(output_dir: Path) -> None:
    """Write a ``_metadata`` file per indicator directory.

    Aggregates row-group statistics (min/max per column, row counts) from every
    parquet file within each indicator subdirectory so that query engines can do
    predicate pushdown without opening individual files.

    Each indicator gets its own ``_metadata`` because indicators have different
    schemas - a single root-level ``_metadata`` is not written.

    Must be called from a **single process** after all
    :class:`ScenarioChunkWriter` instances have been closed.

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
