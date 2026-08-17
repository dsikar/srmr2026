"""
Predictive models for race completion timing and pace estimations.
Includes NaiveLinearModel and TwoTrackModel.
"""

from dataclasses import dataclass
from typing import Optional


def format_hours_to_days(hours: float) -> str:
    """Format decimal hours into readable 'Xd Yh Zm' string."""
    if hours < 0:
        return "0d 0h"
    total_minutes = int(round(hours * 60))
    days = total_minutes // (24 * 60)
    rem_minutes = total_minutes % (24 * 60)
    hrs = rem_minutes // 60
    mins = rem_minutes % 60

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    parts.append(f"{hrs}h")
    if mins > 0:
        parts.append(f"{mins}m")
    return " ".join(parts)


@dataclass
class ModelPrediction:
    model_name: str
    elapsed_hours: float
    remaining_hours: float
    total_hours: float
    days_hours_str: str
    predicted_final_avg_speed_kmh: float
    v_d: Optional[float] = None
    v_h: Optional[float] = None


class BaseRaceModel:
    """Base class for race prediction models."""

    def predict(
        self,
        elapsed_hours: float,
        elapsed_dist_km: float,
        elapsed_ele_m: float,
        total_dist_km: float,
        total_ele_m: float,
    ) -> ModelPrediction:
        raise NotImplementedError


class NaiveLinearModel(BaseRaceModel):
    """
    Naive linear extrapolation based on constant elapsed average speed.
    T = D_total / (d_elapsed / t_elapsed)
    """

    def predict(
        self,
        elapsed_hours: float,
        elapsed_dist_km: float,
        elapsed_ele_m: float,
        total_dist_km: float,
        total_ele_m: float,
    ) -> ModelPrediction:
        if elapsed_hours <= 0 or elapsed_dist_km <= 0:
            # Cannot extrapolate without elapsed movement
            return ModelPrediction(
                model_name="Naive Linear",
                elapsed_hours=elapsed_hours,
                remaining_hours=0.0,
                total_hours=0.0,
                days_hours_str="N/A",
                predicted_final_avg_speed_kmh=0.0,
            )

        current_avg_speed = elapsed_dist_km / elapsed_hours
        predicted_total_hours = total_dist_km / current_avg_speed
        remaining_hours = max(0.0, predicted_total_hours - elapsed_hours)

        return ModelPrediction(
            model_name="Naive Linear",
            elapsed_hours=elapsed_hours,
            remaining_hours=remaining_hours,
            total_hours=predicted_total_hours,
            days_hours_str=format_hours_to_days(predicted_total_hours),
            predicted_final_avg_speed_kmh=current_avg_speed,
        )


class TwoTrackModel(BaseRaceModel):
    """
    Two-Track Decoupled Horizontal/Vertical Work Model.
    T_total = T_distance + T_elevation = (D / v_d) + (H_gain / v_h)
    
    Parameters:
    - v_d: Distance rate / rolling velocity (km/h). Default: 21.5 km/h
    - v_h: Elevation rate / Vertical Ascent Meters per hour (m/h). Default: 450.0 m/h
    """

    def __init__(self, v_d: float = 21.5, v_h: float = 450.0):
        self.v_d = v_d
        self.v_h = v_h

    def calculate_duration(self, distance_km: float, elevation_gain_m: float) -> float:
        """Calculate duration for a segment given distance and elevation gain."""
        t_dist = distance_km / self.v_d if self.v_d > 0 else 0.0
        t_ele = elevation_gain_m / self.v_h if self.v_h > 0 else 0.0
        return t_dist + t_ele

    def predict(
        self,
        elapsed_hours: float,
        elapsed_dist_km: float,
        elapsed_ele_m: float,
        total_dist_km: float,
        total_ele_m: float,
        remaining_dist_km: Optional[float] = None,
        remaining_ele_m: Optional[float] = None,
    ) -> ModelPrediction:
        """
        Predict remaining time and total race duration given progress and upcoming profile.
        """
        if remaining_dist_km is None:
            remaining_dist_km = max(0.0, total_dist_km - elapsed_dist_km)
        if remaining_ele_m is None:
            remaining_ele_m = max(0.0, total_ele_m - elapsed_ele_m)

        remaining_hours = self.calculate_duration(remaining_dist_km, remaining_ele_m)
        predicted_total_hours = elapsed_hours + remaining_hours
        predicted_avg_speed = (
            total_dist_km / predicted_total_hours if predicted_total_hours > 0 else 0.0
        )

        return ModelPrediction(
            model_name="Two-Track (Decoupled)",
            elapsed_hours=elapsed_hours,
            remaining_hours=remaining_hours,
            total_hours=predicted_total_hours,
            days_hours_str=format_hours_to_days(predicted_total_hours),
            predicted_final_avg_speed_kmh=predicted_avg_speed,
            v_d=self.v_d,
            v_h=self.v_h,
        )
