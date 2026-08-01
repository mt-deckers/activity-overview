import os

import yaml

import convert

HERE = os.path.dirname(__file__)


def test_swim_carried_as_raw_hours_monthly():
    """Swim is reported as-is (hours), not converted to km via a pace constant."""
    yml = {
        "2026-06": {"walked": 10, "ran": 5, "cycled": 20, "swam": 7.2},
        "2026-07": {"walked": 0, "ran": 0, "cycled": 0, "swam": 4.7},
    }
    data = convert.build_data(yml)

    idx = {m: i for i, m in enumerate(data["months"])}
    assert data["monthly"]["swam"][idx["2026-06"]] == 7.2
    assert data["monthly"]["swam"][idx["2026-07"]] == 4.7


def test_swim_summed_as_raw_hours_yearly():
    yml = {
        "2026-06": {"walked": 10, "ran": 5, "cycled": 20, "swam": 7.2},
        "2026-07": {"walked": 0, "ran": 0, "cycled": 0, "swam": 4.7},
    }
    data = convert.build_data(yml)

    # 7.2 + 4.7 hours, not the old pace-based ~20.89 km
    assert data["yearly"]["swam"]["2026"] == 7.2 + 4.7


def test_missing_swim_is_none_monthly_and_zero_yearly():
    """Months before swim was tracked have no `swam` key at all."""
    yml = {
        "2024-03": {"walked": 48.77, "ran": 44.89, "cycled": 46.21},
        "2026-06": {"walked": 10, "ran": 5, "cycled": 20, "swam": 7.2},
    }
    data = convert.build_data(yml)

    idx = {m: i for i, m in enumerate(data["months"])}
    assert data["monthly"]["swam"][idx["2024-03"]] is None
    assert data["yearly"]["swam"]["2024"] == 0


def test_zero_becomes_none_monthly():
    """Zero activity renders as a gap (None) in the monthly series."""
    yml = {"2026-08": {"walked": 0, "ran": 0, "cycled": 0, "swam": 0}}
    data = convert.build_data(yml)

    assert data["monthly"]["walked"] == [None]
    assert data["monthly"]["swam"] == [None]


def test_km_activities_unchanged():
    yml = {
        "2026-06": {"walked": 132.64, "ran": 63.74, "cycled": 258.95, "swam": 7.2},
    }
    data = convert.build_data(yml)

    idx = {m: i for i, m in enumerate(data["months"])}
    assert data["monthly"]["walked"][idx["2026-06"]] == 132.64
    assert data["yearly"]["cycled"]["2026"] == 258.95


def test_real_data_yml_end_to_end():
    """Run the actual data.yml through the pipeline (the check that used to be a
    throwaway one-liner). Swim values are the raw logged hours."""
    with open(os.path.join(HERE, "data.yml")) as f:
        yml = yaml.safe_load(f)
    data = convert.build_data(yml)

    idx = {m: i for i, m in enumerate(data["months"])}
    assert data["monthly"]["swam"][idx["2026-06"]] == 7.2
    assert data["monthly"]["swam"][idx["2026-07"]] == 4.7
    assert data["yearly"]["swam"]["2026"] == 7.2 + 4.7
