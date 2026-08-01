import convert_calories as cc


def test_blank_for_zero_missing_negative():
    assert cc.value_to_color(0) is None
    assert cc.value_to_color(None) is None
    assert cc.value_to_color(-50) is None


def test_four_discrete_bands():
    assert cc.value_to_color(1) == cc.UNDER_COLOR      # 1-599   under the weather
    assert cc.value_to_color(300) == cc.UNDER_COLOR
    assert cc.value_to_color(599) == cc.UNDER_COLOR
    assert cc.value_to_color(600) == cc.CRUISE_COLOR   # 600-899 cruising
    assert cc.value_to_color(899) == cc.CRUISE_COLOR
    assert cc.value_to_color(900) == cc.WORK_COLOR     # 900-1400 work
    assert cc.value_to_color(1400) == cc.WORK_COLOR
    assert cc.value_to_color(1401) == cc.MEGA_COLOR    # >1400   MEGA


def test_only_four_colors_ever_emitted():
    palette = {cc.value_to_color(v) for v in range(1, 2500)}
    assert palette == {cc.UNDER_COLOR, cc.CRUISE_COLOR, cc.WORK_COLOR, cc.MEGA_COLOR}


def test_under_the_weather_is_gray():
    hexc = cc.value_to_color(300)  # gray: R, G, B within a narrow range
    r, g, b = (int(hexc[i:i + 2], 16) for i in (1, 3, 5))
    assert max(r, g, b) - min(r, g, b) <= 40


def test_mega_threshold_and_highlight():
    assert cc.value_to_color(1401) == cc.MEGA_COLOR
    data = cc.build_data([("2026-07-31", 1500), ("2026-07-30", 1400), ("2026-07-29", 950)])
    by_date = {d["date"]: d for d in data["days"]}
    assert by_date["2026-07-31"]["highlight"] is True
    assert by_date["2026-07-30"]["highlight"] is False  # 1400 is not mega
    assert by_date["2026-07-29"]["highlight"] is False
    assert data["megaCount"] == 1


def test_privacy_no_raw_value_leaks():
    data = cc.build_data([("2026-07-31", 950), ("2026-07-30", 1500)])
    allowed = {"date", "color", "highlight"}
    for day in data["days"]:
        assert set(day.keys()) == allowed
        # no field anywhere equals a raw calorie number
        assert 950 not in day.values()
        assert 1500 not in day.values()


def test_blank_days_omitted_and_range_sorted():
    data = cc.build_data([
        ("2026-07-31", 950),
        ("2026-07-15", 0),      # blank -> dropped
        ("2026-06-01", 700),
    ])
    dates = [d["date"] for d in data["days"]]
    assert dates == ["2026-06-01", "2026-07-31"]  # sorted, blank omitted
    assert data["start"] == "2026-06-01"
    assert data["end"] == "2026-07-31"


def test_read_csv_skips_header_and_junk(tmp_path):
    p = tmp_path / "export.csv"
    p.write_text(
        "activity_calories_date,activity_calories_value\n"
        "2026-07-31,950\n"
        "\n"                       # blank line
        "2026-07-30,not-a-number\n"
        "2026-07-29,1500\n"
    )
    rows = list(cc.read_csv(str(p)))
    assert rows == [("2026-07-31", 950), ("2026-07-29", 1500)]
