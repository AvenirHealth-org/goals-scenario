import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from avenir_goals_scenario._runner.output import (
    DimNamesMismatchError,
    DimSpec,
    UnknownIndicatorError,
    _to_long_table,
    consolidate_metadata,
    write_scenario_results,
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
# write_scenario_results - partition paths
# ---------------------------------------------------------------------------


def test_partition_path(tmp_path):
    sim_output = [{"p_hivpop": np.asfortranarray(np.ones((3, 2)))}]
    indicator_dims = {
        "p_hivpop": (DimSpec("age"), DimSpec("sex", labels=["male", "female"])),
    }
    write_scenario_results(
        scenario_id=7,
        pjnz_name="Zimbabwe",
        sim_output=sim_output,
        output_dir=tmp_path,
        indicator_dims=indicator_dims,
    )
    expected = tmp_path / "p_hivpop" / "pjnz_name=Zimbabwe" / "scenario_id=7" / "part-0.parquet"
    assert expected.exists()


def test_unknown_indicator_error_suggests_close_match():
    err = UnknownIndicatorError("p_hiv_pop", supported=["p_hivpop", "p_infections", "h_artpop"])
    assert "p_hivpop" in str(err)
    assert "Did you mean" in str(err)


def test_unknown_indicator_error_lists_all_when_no_close_match():
    err = UnknownIndicatorError("zzz_nothing", supported=["p_hivpop", "p_infections"])
    assert "Supported indicators" in str(err)
    assert "p_hivpop" in str(err)


def test_unknown_indicator_error(tmp_path):
    sim_output = [{"p_hivpop": np.asfortranarray(np.ones((3, 2)))}]
    with pytest.raises(UnknownIndicatorError):
        write_scenario_results(
            scenario_id=1,
            pjnz_name="Zimbabwe",
            sim_output=sim_output,
            output_dir=tmp_path,
            indicator_dims={},
        )


def test_write_multiple_indicators(tmp_path):
    sim_output = [
        {
            "p_hivpop": np.asfortranarray(np.ones((3, 2))),
            "p_infections": np.asfortranarray(np.ones((3, 2))),
        }
    ]
    indicator_dims = {
        "p_hivpop": (DimSpec("age"), DimSpec("sex", labels=["male", "female"])),
        "p_infections": (DimSpec("age"), DimSpec("sex", labels=["male", "female"])),
    }
    write_scenario_results(
        scenario_id=1,
        pjnz_name="Kenya",
        sim_output=sim_output,
        output_dir=tmp_path,
        indicator_dims=indicator_dims,
    )
    assert (tmp_path / "p_hivpop" / "pjnz_name=Kenya" / "scenario_id=1" / "part-0.parquet").exists()
    assert (tmp_path / "p_infections" / "pjnz_name=Kenya" / "scenario_id=1" / "part-0.parquet").exists()


def test_write_roundtrip(tmp_path):
    n_sims = 3
    shape = (5, 2)
    arrays = _f(shape, n_sims)
    sim_output = [{"p_hivpop": a} for a in arrays]
    indicator_dims = {
        "p_hivpop": (DimSpec("age"), DimSpec("sex", labels=["male", "female"])),
    }
    write_scenario_results(
        scenario_id=1,
        pjnz_name="Zambia",
        sim_output=sim_output,
        output_dir=tmp_path,
        indicator_dims=indicator_dims,
    )
    path = tmp_path / "p_hivpop" / "pjnz_name=Zambia" / "scenario_id=1" / "part-0.parquet"
    table = pq.read_table(path)
    assert len(table) == n_sims * shape[0] * shape[1]
    # read_table adds hive partition columns; check only the data columns
    assert [f for f in table.schema.names if f not in ("pjnz_name", "scenario_id")] == [
        "age",
        "sex",
        "simulation",
        "value",
    ]


# ---------------------------------------------------------------------------
# consolidate_metadata
# ---------------------------------------------------------------------------


def _write_indicator(tmp_path, shape):
    sim_output = [{"p_hivpop": np.asfortranarray(np.ones(shape))}]
    indicator_dims = {"p_hivpop": tuple(DimSpec(f"d{i}") for i in range(len(shape)))}
    write_scenario_results(
        scenario_id=1,
        pjnz_name="Kenya",
        sim_output=sim_output,
        output_dir=tmp_path,
        indicator_dims=indicator_dims,
    )


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
