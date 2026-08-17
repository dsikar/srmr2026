"""
Thermoregulatory & Altitude Temperature Coupling Model (External Factors Only).

Models altitude-dependent ambient temperature T(h), metabolic thermoregulation
power overhead P_thermo(T), and mechanical power coupling via Kirchhoff circuit analogy.
"""

from dataclasses import dataclass
import math
from typing import Dict, List, Tuple
import numpy as np


# Route altitude bounds (meters)
ALT_MIN_M = 933.0
ALT_MAX_M = 3918.0

# Temperature boundary values (°C)
TEMP_BASE_C = 40.0   # At lowest altitude (933 m)
TEMP_MIN_C = 0.0     # At highest altitude (3918 m)

# Environmental Lapse Rate: Γ = (40 - 0) / (3918 - 933) = 0.0134003 °C/m
LAPSE_RATE_GAMMA = (TEMP_BASE_C - TEMP_MIN_C) / (ALT_MAX_M - ALT_MIN_M)

# Physiological Thermoneutral Zone (°C)
T_LOWER_C = 18.0
T_UPPER_C = 22.0

# Gross sustainable metabolic power capacity (Watts)
P_SUSTAINABLE_WATTS = 250.0

# Baseline thermoregulation coefficient parameters (Watts per (°C)^2 offset)
K_HEAT_WATTS_PER_C2 = 0.35  # Heat dissipation overhead (vasodilation, sweating, cardiac drift)
K_COLD_WATTS_PER_C2 = 0.25  # Cold defense overhead (shivering/non-shivering thermogenesis)


def calculate_ambient_temperature(altitude_m: float) -> float:
    """
    Calculate ambient temperature T(h) in °C as a continuous function of altitude h.
    T(h) = T_base - Γ * (h - h_min)
    """
    h_clamped = max(ALT_MIN_M, min(ALT_MAX_M, altitude_m))
    t_h = TEMP_BASE_C - LAPSE_RATE_GAMMA * (h_clamped - ALT_MIN_M)
    return float(t_h)


def calculate_thermo_power_overhead(temp_c: float) -> float:
    """
    Calculate metabolic thermoregulation power overhead P_thermo(T) in Watts.
    P_thermo = 0 in thermoneutral zone [18°C, 22°C].
    P_thermo = k_heat * (T - 22)^2 for T > 22°C.
    P_thermo = k_cold * (18 - T)^2 for T < 18°C.
    """
    if temp_c > T_UPPER_C:
        delta_t = temp_c - T_UPPER_C
        return K_HEAT_WATTS_PER_C2 * (delta_t ** 2)
    elif temp_c < T_LOWER_C:
        delta_t = T_LOWER_C - temp_c
        return K_COLD_WATTS_PER_C2 * (delta_t ** 2)
    else:
        return 0.0


def calculate_available_mechanical_power(altitude_m: float) -> Tuple[float, float, float]:
    """
    Returns (temp_c, p_thermo_watts, p_mechanical_watts).
    P_mechanical = P_sustainable - P_thermo
    """
    temp_c = calculate_ambient_temperature(altitude_m)
    p_thermo = calculate_thermo_power_overhead(temp_c)
    p_mech = max(50.0, P_SUSTAINABLE_WATTS - p_thermo)
    return temp_c, p_thermo, p_mech


@dataclass
class ThermoBudgetReport:
    days1_2_elapsed_hours: float
    days1_2_dist_km: float
    days1_2_paid_energy_kcal: float
    days1_2_paid_thermo_kcal: float
    remaining_dist_km: float
    remaining_proj_hours: float
    remaining_proj_energy_kcal: float
    remaining_proj_thermo_kcal: float
    net_adjusted_avg_speed_kmh: float
    highest_penalty_sector: str
    highest_penalty_detail: str


def evaluate_thermo_budget(
    elevations_m: np.ndarray,
    distances_km: np.ndarray,
    checkpoint_idx: int,
    base_v_d: float = 21.5,
    base_v_h: float = 450.0,
) -> ThermoBudgetReport:
    """
    Evaluates energy paid (Days 1-2) vs projected remaining energy demand,
    accounting for Kirchhoff-style metabolic power dissipation.
    """
    # 1. Evaluate historical segment (0 to checkpoint)
    paid_thermo_joules = 0.0
    paid_mech_joules = 0.0
    paid_hours = 51.0

    # Calculate average altitude across Days 1-2 profile
    cp_elevs = elevations_m[:checkpoint_idx+1]
    avg_alt_cp = float(np.mean(cp_elevs))
    temp_cp, p_thermo_cp, p_mech_cp = calculate_available_mechanical_power(avg_alt_cp)

    paid_thermo_joules = p_thermo_cp * (paid_hours * 3600.0)
    paid_mech_joules = p_mech_cp * (paid_hours * 3600.0)

    paid_thermo_kcal = paid_thermo_joules / 4184.0
    paid_total_kcal = (paid_thermo_joules + paid_mech_joules) / 4184.0

    # 2. Evaluate remaining profile (checkpoint to finish)
    rem_elevs = elevations_m[checkpoint_idx:]
    rem_dists = distances_km[checkpoint_idx:] - distances_km[checkpoint_idx]

    # Sector 2 (600-1400 km) and Sector 3 (1400-2062 km) analysis
    # Sector 2 average altitude ~ 2000m -> T ~ 25°C -> slight heat overhead
    # Sector 3 average altitude ~ 3200m -> T ~ 9°C -> cold defense + extreme climbing gradient
    avg_alt_rem = float(np.mean(rem_elevs))
    temp_rem, p_thermo_rem, p_mech_rem = calculate_available_mechanical_power(avg_alt_rem)

    # Speed attenuation ratio due to thermal dissipation
    thermal_power_ratio = p_mech_rem / P_SUSTAINABLE_WATTS

    # Adjusted remaining velocities
    adj_v_d = base_v_d * math.sqrt(thermal_power_ratio)
    adj_v_h = base_v_h * thermal_power_ratio

    rem_dist_km = float(distances_km[-1] - distances_km[checkpoint_idx])
    rem_ele_m = float(np.sum(np.maximum(0.0, np.diff(rem_elevs))))

    rem_hours = (rem_dist_km / adj_v_d) + (rem_ele_m / adj_v_h)

    proj_thermo_joules = p_thermo_rem * (rem_hours * 3600.0)
    proj_mech_joules = p_mech_rem * (rem_hours * 3600.0)

    proj_thermo_kcal = proj_thermo_joules / 4184.0
    proj_total_kcal = (proj_thermo_joules + proj_mech_joules) / 4184.0

    total_hours = paid_hours + rem_hours
    net_avg_speed = distances_km[-1] / total_hours

    sector3_detail = (
        "Sector 3 (1,400–2,062 km): High Mountain Passes (elevations >3,500 m, "
        "ambient temperatures T < 5°C causing cold thermogenesis overhead, combined with "
        "brutal 28.5 m/km climbing density)."
    )

    return ThermoBudgetReport(
        days1_2_elapsed_hours=paid_hours,
        days1_2_dist_km=float(distances_km[checkpoint_idx]),
        days1_2_paid_energy_kcal=paid_total_kcal,
        days1_2_paid_thermo_kcal=paid_thermo_kcal,
        remaining_dist_km=rem_dist_km,
        remaining_proj_hours=rem_hours,
        remaining_proj_energy_kcal=proj_total_kcal,
        remaining_proj_thermo_kcal=proj_thermo_kcal,
        net_adjusted_avg_speed_kmh=net_avg_speed,
        highest_penalty_sector="Sector 3 (High Mountain Passes: 1,400–2,062 km)",
        highest_penalty_detail=sector3_detail,
    )
