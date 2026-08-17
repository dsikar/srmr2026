"""
Calibration module for optimizing (v_d, v_h) parameters from historical checkpoint data.
Uses bounded least-squares optimization via scipy.optimize.minimize.
"""

from dataclasses import dataclass
from typing import List, Tuple
import numpy as np
from scipy.optimize import minimize


@dataclass
class CalibrationResult:
    v_d: float
    v_h: float
    rmse_hours: float
    message: str


def calibrate_coefficients(
    checkpoints: List[dict],
    default_v_d: float = 21.5,
    default_v_h: float = 450.0,
    v_d_bounds: Tuple[float, float] = (15.0, 30.0),
    v_h_bounds: Tuple[float, float] = (250.0, 650.0),
) -> CalibrationResult:
    """
    Calibrates (v_d, v_h) using bounded least-squares regression from checkpoint history.

    Checkpoints schema:
    [
        {"elapsed_hours": float, "distance_km": float, "elevation_gain_m": float},
        ...
    ]
    """
    if not checkpoints:
        return CalibrationResult(
            v_d=default_v_d,
            v_h=default_v_h,
            rmse_hours=0.0,
            message="No checkpoints provided; returning initial default coefficients.",
        )

    # Extract checkpoint arrays
    times = np.array([cp["elapsed_hours"] for cp in checkpoints], dtype=float)
    dists = np.array([cp["distance_km"] for cp in checkpoints], dtype=float)
    eles = np.array([cp["elevation_gain_m"] for cp in checkpoints], dtype=float)

    # Filter out initial start point (0, 0, 0) if present to avoid division issues
    valid_mask = (times > 0) & (dists > 0)
    times = times[valid_mask]
    dists = dists[valid_mask]
    eles = eles[valid_mask]

    if len(times) == 0:
        return CalibrationResult(
            v_d=default_v_d,
            v_h=default_v_h,
            rmse_hours=0.0,
            message="No non-zero checkpoints found; returning default coefficients.",
        )

    # Loss function: Sum of Squared Errors + small regularization toward prior (default_v_d, default_v_h)
    def objective(params):
        v_d, v_h = params
        pred_times = (dists / v_d) + (eles / v_h)
        residuals = times - pred_times
        sse = np.sum(residuals**2)
        # Prior regularization penalty (weak weight)
        prior_penalty = 1e-4 * ((v_d - default_v_d) ** 2 + ((v_h - default_v_h) / 100.0) ** 2)
        return sse + prior_penalty

    initial_guess = [default_v_d, default_v_h]
    bounds = [v_d_bounds, v_h_bounds]

    res = minimize(objective, initial_guess, method="L-BFGS-B", bounds=bounds)

    opt_v_d, opt_v_h = float(res.x[0]), float(res.x[1])
    pred_times = (dists / opt_v_d) + (eles / opt_v_h)
    rmse = float(np.sqrt(np.mean((times - pred_times) ** 2)))

    return CalibrationResult(
        v_d=opt_v_d,
        v_h=opt_v_h,
        rmse_hours=rmse,
        message=res.message if hasattr(res, "message") else "Optimization completed.",
    )
