import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from avenir_goals_scenario._runner.output import (
    DimNamesMismatchError,
    DimSpec,
    ScenarioChunkWriter,
    UnknownIndicatorError,
    _to_long_table,
    consolidate_metadata,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _f(shape, n_sims=3, seed=0):
    """Return n_sims F-contiguous float64 arrays of the given shape."""
    rng = np.random.default_rng(seed)
    return [np.asfortranarray(rng.random(shape)) for _ in range(n_sims)]


# ---------------------------------------------------------------------------
# _to_long_table - schema
# ---------------------------------------------------------------------------


def test_schema_plain_dims():
    arrays = _f((4, 5))
    table = _to_long_table(arrays, (DimSpec("age"), DimSpec("year")))
    assert table.schema.names == ["age", "year", "simulation", "value"]
    assert table.schema.field("age").type == pa.int16()
    assert table.schema.field("year").type == pa.int16()
    assert table.schema.field("simulation").type == pa.int32()
    assert table.schema.field("value").type == pa.float64()


def test_schema_dict_dim():
    arrays = _f((4, 2))
    specs = (DimSpec("age"), DimSpec("sex", labels=["male", "female"]))
    table = _to_long_table(arrays, specs)
    sex_type = table.schema.field("sex").type
    assert pa.types.is_dictionary(sex_type)
    assert sex_type.value_type == pa.utf8()


def test_schema_string_shorthand():
    arrays = _f((3, 4))
    table = _to_long_table(arrays, ("age", "year"))
    assert table.schema.names == ["age", "year", "simulation", "value"]


# ---------------------------------------------------------------------------
# _to_long_table - row count and column order
# ---------------------------------------------------------------------------


def test_row_count():
    n_sims = 5
    shape = (3, 4, 7)
    arrays = _f(shape, n_sims)
    table = _to_long_table(arrays, ("a", "b", "c"))
    assert len(table) == n_sims * 3 * 4 * 7


def test_column_order():
    arrays = _f((81, 2, 50))
    specs = (
        DimSpec("age"),
        DimSpec("sex", labels=["male", "female"]),
        DimSpec("year", offset=2010),
    )
    table = _to_long_table(arrays, specs)
    assert table.schema.names == ["age", "sex", "year", "simulation", "value"]


# ---------------------------------------------------------------------------
# _to_long_table - row order (first dim varies fastest, F-order)
# ---------------------------------------------------------------------------


def test_first_dim_varies_fastest():
    """With F-order output, age (axis 0) should cycle through 0..n-1 first."""
    n_age, n_year = 5, 3
    arrays = _f((n_age, n_year), n_sims=1)
    table = _to_long_table(arrays, ("age", "year"))
    age_col = table.column("age").to_pylist()
    # First n_age values should be 0,1,2,...,n_age-1 (age cycling fastest)
    assert age_col[:n_age] == list(range(n_age))


def test_last_dim_varies_slowest():
    n_age, n_year = 4, 3
    arrays = _f((n_age, n_year), n_sims=1)
    table = _to_long_table(arrays, ("age", "year"))
    year_col = table.column("year").to_pylist()
    # year should repeat n_age times before incrementing
    assert year_col[:n_age] == [0] * n_age
    assert year_col[n_age : 2 * n_age] == [1] * n_age


# ---------------------------------------------------------------------------
# _to_long_table - values
# ---------------------------------------------------------------------------


def test_values_match_f_ravel():
    n_sims = 2
    arrays = _f((3, 4), n_sims)
    table = _to_long_table(arrays, ("a", "b"))
    expected = np.concatenate([a.ravel(order="F") for a in arrays])
    np.testing.assert_array_equal(table.column("value").to_pylist(), expected)


def test_single_sim_values():
    arr = np.asfortranarray(np.arange(6, dtype=float).reshape((2, 3), order="F"))
    table = _to_long_table([arr], ("row", "col"))
    np.testing.assert_array_equal(table.column("value").to_pylist(), arr.ravel(order="F"))


# ---------------------------------------------------------------------------
# _to_long_table - offset
# ---------------------------------------------------------------------------


def test_year_offset():
    arrays = _f((3, 5), n_sims=1)
    specs = (DimSpec("age"), DimSpec("year", offset=2010))
    table = _to_long_table(arrays, specs)
    year_col = table.column("year").to_pylist()
    assert min(year_col) == 2010
    assert max(year_col) == 2014


# ---------------------------------------------------------------------------
# _to_long_table - simulation column
# ---------------------------------------------------------------------------


def test_simulation_column():
    n_sims = 4
    shape = (3, 2)
    n_per_sim = 6
    arrays = _f(shape, n_sims)
    table = _to_long_table(arrays, ("a", "b"))
    sim_col = table.column("simulation").to_pylist()
    expected = [s for s in range(n_sims) for _ in range(n_per_sim)]
    assert sim_col == expected


# ---------------------------------------------------------------------------
# _to_long_table - error cases
# ---------------------------------------------------------------------------


def test_dim_names_mismatch():
    arrays = _f((3, 4))
    with pytest.raises(DimNamesMismatchError):
        _to_long_table(arrays, ("only_one",))


def test_dim_names_too_many():
    arrays = _f((3, 4))
    with pytest.raises(DimNamesMismatchError):
        _to_long_table(arrays, ("a", "b", "c"))


# ---------------------------------------------------------------------------
# _to_long_table - scenario_id column
# ---------------------------------------------------------------------------


def test_scenario_id_column_prepended():
    arrays = _f((3, 2), n_sims=2)
    table = _to_long_table(arrays, ("age", "sex"), scenario_id="7")
    assert table.schema.names == ["scenario_id", "age", "sex", "simulation", "value"]
    assert table.schema.field("scenario_id").type == pa.utf8()
    assert set(table.column("scenario_id").to_pylist()) == {"7"}


def test_scenario_id_column_absent_by_default():
    arrays = _f((3, 2), n_sims=2)
    table = _to_long_table(arrays, ("age", "sex"))
    assert "scenario_id" not in table.schema.names


# ---------------------------------------------------------------------------
# ScenarioChunkWriter - streaming layout
# ---------------------------------------------------------------------------

_DIMS_2D = {
    "p_hivpop": (DimSpec("age"), DimSpec("sex", labels=["male", "female"])),
    "p_infections": (DimSpec("age"), DimSpec("sex", labels=["male", "female"])),
}


def _sim(indicators, shape=(3, 2)):
    return {ind: np.asfortranarray(np.ones(shape)) for ind in indicators}


def test_chunk_writer_one_file_per_indicator(tmp_path):
    writer = ScenarioChunkWriter(tmp_path, "Kenya", "part-0", _DIMS_2D)
    writer.write_scenario("1", [_sim(["p_hivpop", "p_infections"])])
    writer.write_scenario("2", [_sim(["p_hivpop", "p_infections"])])
    writer.close()

    for indicator in ("p_hivpop", "p_infections"):
        part_dir = tmp_path / indicator / "pjnz_name=Kenya"
        assert [p.name for p in part_dir.glob("*.parquet")] == ["part-0.parquet"]


def test_chunk_writer_scenarios_share_file_as_row_groups(tmp_path):
    writer = ScenarioChunkWriter(tmp_path, "Kenya", "part-0", _DIMS_2D)
    for sid in ("1", "2", "3"):
        writer.write_scenario(sid, [_sim(["p_hivpop"])])
    writer.close()

    path = tmp_path / "p_hivpop" / "pjnz_name=Kenya" / "part-0.parquet"
    pf = pq.ParquetFile(path)
    # One row group per scenario keeps scenario_id predicate pushdown precise.
    assert pf.num_row_groups == 3
    table = pf.read()
    assert set(table.column("scenario_id").to_pylist()) == {"1", "2", "3"}
    assert [f for f in table.schema.names if f != "pjnz_name"] == [
        "scenario_id",
        "age",
        "sex",
        "simulation",
        "value",
    ]


def test_chunk_writer_row_count(tmp_path):
    n_sims = 3
    shape = (5, 2)
    writer = ScenarioChunkWriter(tmp_path, "Zambia", "part-0", {"p_hivpop": (DimSpec("age"), DimSpec("sex"))})
    writer.write_scenario("1", [{"p_hivpop": a} for a in _f(shape, n_sims)])
    writer.close()
    table = pq.read_table(tmp_path / "p_hivpop" / "pjnz_name=Zambia" / "part-0.parquet")
    assert len(table) == n_sims * shape[0] * shape[1]


def test_chunk_writer_unknown_indicator_raises(tmp_path):
    writer = ScenarioChunkWriter(tmp_path, "Zimbabwe", "part-0", {})
    with pytest.raises(UnknownIndicatorError):
        writer.write_scenario("1", [_sim(["p_hivpop"])])


def test_chunk_writer_staging_copies_to_output(tmp_path):
    output_dir = tmp_path / "out"
    staging_dir = tmp_path / "stage"
    output_dir.mkdir()
    writer = ScenarioChunkWriter(
        output_dir, "Kenya", "part-0", {"p_hivpop": (DimSpec("age"), DimSpec("sex"))}, staging_dir=staging_dir
    )
    writer.write_scenario("1", [_sim(["p_hivpop"])])
    writer.close()
    final = output_dir / "p_hivpop" / "pjnz_name=Kenya" / "part-0.parquet"
    assert final.exists()
    # Staged copy has been moved, not left behind.
    assert not (staging_dir / "p_hivpop" / "pjnz_name=Kenya" / "part-0.parquet").exists()


def test_chunk_writer_abort_removes_part_file(tmp_path):
    writer = ScenarioChunkWriter(tmp_path, "Kenya", "part-0", {"p_hivpop": (DimSpec("age"), DimSpec("sex"))})
    writer.write_scenario("1", [_sim(["p_hivpop"])])
    writer.abort()
    assert not (tmp_path / "p_hivpop" / "pjnz_name=Kenya" / "part-0.parquet").exists()


def test_custom_part_name_for_retry(tmp_path):
    writer = ScenarioChunkWriter(
        tmp_path, "Kenya", "part-retry-abc123-0", {"p_hivpop": (DimSpec("age"), DimSpec("sex"))}
    )
    writer.write_scenario("1", [_sim(["p_hivpop"])])
    writer.close()
    assert (tmp_path / "p_hivpop" / "pjnz_name=Kenya" / "part-retry-abc123-0.parquet").exists()


def test_unknown_indicator_error_suggests_close_match():
    err = UnknownIndicatorError("p_hiv_pop", supported=["p_hivpop", "p_infections", "h_artpop"])
    assert "p_hivpop" in str(err)
    assert "Did you mean" in str(err)


def test_unknown_indicator_error_lists_all_when_no_close_match():
    err = UnknownIndicatorError("zzz_nothing", supported=["p_hivpop", "p_infections"])
    assert "Supported indicators" in str(err)
    assert "p_hivpop" in str(err)


# ---------------------------------------------------------------------------
# consolidate_metadata
# ---------------------------------------------------------------------------


def _write_indicator(tmp_path, shape):
    indicator_dims = {"p_hivpop": tuple(DimSpec(f"d{i}") for i in range(len(shape)))}
    writer = ScenarioChunkWriter(tmp_path, "Kenya", "part-0", indicator_dims)
    writer.write_scenario("1", [{"p_hivpop": np.asfortranarray(np.ones(shape))}])
    writer.close()


def test_consolidate_metadata_writes_per_indicator(tmp_path):
    _write_indicator(tmp_path, (3, 2))
    consolidate_metadata(tmp_path)
    assert (tmp_path / "p_hivpop" / "_metadata").exists()


def test_consolidate_metadata_skips_empty_indicator_dir(tmp_path):
    _write_indicator(tmp_path, (3, 2))
    # Create an indicator directory with no parquet files
    (tmp_path / "empty_indicator").mkdir()
    consolidate_metadata(tmp_path)
    assert not (tmp_path / "empty_indicator" / "_metadata").exists()
    assert (tmp_path / "p_hivpop" / "_metadata").exists()


def test_consolidate_metadata_warns_when_no_dirs(tmp_path):
    consolidate_metadata(tmp_path)  # should not raise


def test_consolidate_metadata_raises_on_schema_mismatch(tmp_path):
    indicator_dir = tmp_path / "p_hivpop"

    part1 = indicator_dir / "pjnz_name=Kenya" / "scenario_id=1"
    part1.mkdir(parents=True)
    schema_v1 = pa.schema([pa.field("age", pa.int16()), pa.field("value", pa.float64())])
    pq.write_table(
        pa.table({"age": pa.array([1, 2], type=pa.int16()), "value": pa.array([1.0, 2.0])}, schema=schema_v1),
        part1 / "part-0.parquet",
    )

    part2 = indicator_dir / "pjnz_name=Zambia" / "scenario_id=1"
    part2.mkdir(parents=True)
    schema_v2 = pa.schema([pa.field("age", pa.int32()), pa.field("value", pa.float64())])
    pq.write_table(
        pa.table({"age": pa.array([1, 2], type=pa.int32()), "value": pa.array([1.0, 2.0])}, schema=schema_v2),
        part2 / "part-0.parquet",
    )

    with pytest.raises(ValueError, match="Schema mismatch"):
        consolidate_metadata(tmp_path)
