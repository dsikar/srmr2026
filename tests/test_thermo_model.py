"""
Unit tests for thermoregulatory and altitude temperature coupling model.
"""

import numpy as np
import pytest

from src.thermo_model import (
    ALT_MAX_M,
    ALT_MIN_M,
    calculate_ambient_temperature,
    calculate_available_mechanical_power,
    calculate_thermo_power_overhead,
    evaluate_thermo_budget,
)


def test_ambient_temperature_lapse_rate():
    # At min altitude 933m -> 40°C
    assert pytest.approx(calculate_ambient_temperature(ALT_MIN_M), abs=0.1) == 40.0
    # At max altitude 3918m -> 0°C
    assert pytest.approx(calculate_ambient_temperature(ALT_MAX_M), abs=0.1) == 0.0
    # Midpoint (approx 2425m) -> 20°C
    mid_alt = (ALT_MIN_M + ALT_MAX_M) / 2.0
    assert pytest.approx(calculate_ambient_temperature(mid_alt), abs=0.5) == 20.0


def test_thermo_power_overhead():
    # Thermoneutral zone [18°C, 22°C]
    assert calculate_thermo_power_overhead(20.0) == 0.0
    assert calculate_thermo_power_overhead(18.0) == 0.0
    assert calculate_thermo_power_overhead(22.0) == 0.0

    # Heat dissipation overhead (30°C)
    p_heat = calculate_thermo_power_overhead(30.0)
    assert p_heat > 0.0

    # Cold defense overhead (5°C)
    p_cold = calculate_thermo_power_overhead(5.0)
    assert p_cold > 0.0


def test_evaluate_thermo_budget():
    elevations = np.linspace(1000.0, 3500.0, 100)
    distances = np.linspace(0.0, 2062.0, 100)
    cp_idx = 32  # Approx 657 km

    report = evaluate_thermo_budget(elevations, distances, cp_idx)

    assert report.days1_2_elapsed_hours == 51.0
    assert report.remaining_dist_km > 1300.0
    assert report.net_adjusted_avg_speed_kmh > 0.0
    assert "Sector 3" in report.highest_penalty_sector
