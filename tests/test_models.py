"""
Unit tests for models, calibration, and CLI time parsing.
"""

import pytest

from main import parse_time_string
from src.calibration import calibrate_coefficients
from src.models import NaiveLinearModel, TwoTrackModel, format_hours_to_days


def test_format_hours_to_days():
    assert format_hours_to_days(177.0) == "7d 9h"
    assert format_hours_to_days(51.0) == "2d 3h"
    assert format_hours_to_days(0.0) == "0h"


def test_naive_linear_model():
    model = NaiveLinearModel()

    # Day 2 + 3h (51h elapsed, 657km covered out of 2062km)
    pred = model.predict(
        elapsed_hours=51.0,
        elapsed_dist_km=657.0,
        elapsed_ele_m=9200.0,
        total_dist_km=2062.0,
        total_ele_m=36490.0,
    )

    # Naive speed = 657 / 51 = 12.882 km/h
    # Naive total hours = 2062 / 12.882 = 160.06 hours
    assert pytest.approx(pred.predicted_final_avg_speed_kmh, abs=0.01) == 12.88
    assert pytest.approx(pred.total_hours, abs=0.5) == 160.06
    assert pred.days_hours_str.startswith("6d 16h")


def test_two_track_model_baseline():
    model = TwoTrackModel(v_d=21.5, v_h=450.0)

    # Full course calculation: 2062 km, 36490 m gain
    # T_dist = 2062 / 21.5 = 95.907 h
    # T_ele = 36490 / 450 = 81.089 h
    # T_total = 176.996 h (~177.0 h)
    duration = model.calculate_duration(2062.0, 36490.0)
    assert pytest.approx(duration, abs=0.1) == 177.0

    # Prediction from Day 2 + 3h checkpoint (51h elapsed, 657km, 9200m)
    rem_dist = 2062.0 - 657.0  # 1405 km
    rem_ele = 36490.0 - 9200.0  # 27290 m

    pred = model.predict(
        elapsed_hours=51.0,
        elapsed_dist_km=657.0,
        elapsed_ele_m=9200.0,
        total_dist_km=2062.0,
        total_ele_m=36490.0,
        remaining_dist_km=rem_dist,
        remaining_ele_m=rem_ele,
    )

    assert pytest.approx(pred.total_hours, abs=0.2) == 177.0
    assert pred.days_hours_str == "7d 9h"
    assert pytest.approx(pred.predicted_final_avg_speed_kmh, abs=0.05) == 11.65


def test_calibrate_coefficients():
    checkpoints = [
        {"elapsed_hours": 51.0, "distance_km": 657.0, "elevation_gain_m": 9200.0}
    ]
    res = calibrate_coefficients(checkpoints)

    assert 15.0 <= res.v_d <= 30.0
    assert 250.0 <= res.v_h <= 650.0
    # Coefficients should stay near default baseline for 1 checkpoint
    assert pytest.approx(res.v_d, abs=2.0) == 21.5
    assert pytest.approx(res.v_h, abs=50.0) == 450.0


def test_parse_time_string():
    assert parse_time_string("2d 3h") == 51.0
    assert parse_time_string("51") == 51.0
    assert parse_time_string("51.5") == 51.5
    assert parse_time_string("1d 12h 30m") == 36.5
    assert parse_time_string(" 2d  3h ") == 51.0
