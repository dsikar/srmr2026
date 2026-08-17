"""
Unit tests for gpx_parser module.
"""

from pathlib import Path
import numpy as np
import pytest

from src.gpx_parser import (
    DEFAULT_COURSE_DISTANCE_KM,
    DEFAULT_COURSE_ELEVATION_GAIN_M,
    get_remaining_metrics,
    haversine_distance,
    parse_gpx_file,
    smooth_elevations,
)

GPX_PATH = "data/gpx/Silk_Road_Mountain_Race_2026.gpx"


def test_haversine_distance():
    # Distance between London (51.5074, -0.1278) and Paris (48.8566, 2.3522) is approx 344 km
    dist = haversine_distance(51.5074, -0.1278, 48.8566, 2.3522)
    assert pytest.approx(dist, rel=0.02) == 343.5


def test_smooth_elevations():
    raw_elevations = np.array([100.0, 105.0, 95.0, 110.0, 90.0, 100.0])
    smoothed = smooth_elevations(raw_elevations, window_size=3)
    assert len(smoothed) == len(raw_elevations)
    assert isinstance(smoothed, np.ndarray)


def test_get_remaining_metrics_fallback():
    # At start (0 km), remaining distance and elevation gain should equal baseline total
    rem_d, rem_h = get_remaining_metrics(0.0, gpx_path="non_existent.gpx")
    assert rem_d == DEFAULT_COURSE_DISTANCE_KM
    assert rem_h == DEFAULT_COURSE_ELEVATION_GAIN_M

    # At end (2062 km), remaining distance and gain should be 0
    rem_d_end, rem_h_end = get_remaining_metrics(DEFAULT_COURSE_DISTANCE_KM, gpx_path="non_existent.gpx")
    assert rem_d_end == 0.0
    assert rem_h_end == 0.0


@pytest.mark.skipif(not Path(GPX_PATH).exists(), reason="GPX file not found")
def test_parse_gpx_file():
    metrics = parse_gpx_file(GPX_PATH)
    assert metrics.total_distance_km > 1500.0  # Course is ~2062 km
    assert metrics.total_elevation_gain_m > 20000.0  # Gain ~36,490 m
    assert len(metrics.sectors) == 3
    assert not metrics.points_df.empty
