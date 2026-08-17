"""
GPX Parser module for SRMR Race Tracker.
Parses GPX tracks, computes haversine distances, applies elevation smoothing,
extracts slope profiles, sector metrics, and remaining course metrics.
"""

from dataclasses import dataclass
import math
from pathlib import Path
from typing import List, Optional, Tuple

import gpxpy
import gpxpy.gpx
import numpy as np
import pandas as pd


# Default course metrics for SRMR 2026 if GPX track is absent
DEFAULT_COURSE_DISTANCE_KM = 2062.0
DEFAULT_COURSE_ELEVATION_GAIN_M = 36490.0


@dataclass
class SectorProfile:
    name: str
    start_km: float
    end_km: float
    distance_km: float
    elevation_gain_m: float
    climbing_density_m_per_km: float
    avg_gradient_pct: float


@dataclass
class TrackMetrics:
    total_distance_km: float
    total_elevation_gain_m: float
    total_elevation_loss_m: float
    min_elevation_m: float
    max_elevation_m: float
    points_df: pd.DataFrame
    sectors: List[SectorProfile]


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance between two points in km."""
    r = 6371.0  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2.0) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return r * c


def smooth_elevations(elevations: np.ndarray, window_size: int = 5) -> np.ndarray:
    """
    Apply a rolling mean smoothing filter to elevation data to reduce GPS noise.
    """
    if len(elevations) < window_size:
        return elevations
    series = pd.Series(elevations)
    smoothed = series.rolling(window=window_size, min_periods=1, center=True).mean()
    return smoothed.to_numpy()


def parse_gpx_file(
    gpx_path: str, smoothing_window: int = 5
) -> TrackMetrics:
    """
    Parse GPX file and compute cumulative metrics, smoothed elevation, and sector profiles.
    """
    path = Path(gpx_path)
    if not path.exists():
        raise FileNotFoundError(f"GPX file not found at: {gpx_path}")

    with open(path, "r", encoding="utf-8") as f:
        gpx = gpxpy.parse(f)

    points_data = []
    total_dist = 0.0

    for track in gpx.tracks:
        for segment in track.segments:
            for i, point in enumerate(segment.points):
                ele = point.elevation if point.elevation is not None else 0.0
                if i == 0 and not points_data:
                    dist_delta = 0.0
                else:
                    prev_lat = points_data[-1]["lat"]
                    prev_lon = points_data[-1]["lon"]
                    dist_delta = haversine_distance(prev_lat, prev_lon, point.latitude, point.longitude)

                total_dist += dist_delta
                points_data.append({
                    "lat": point.latitude,
                    "lon": point.longitude,
                    "elevation_raw": ele,
                    "segment_dist_km": dist_delta,
                    "cum_dist_km": total_dist,
                })

    if not points_data:
        raise ValueError(f"No points found in GPX file: {gpx_path}")

    df = pd.DataFrame(points_data)

    # Smooth elevations
    raw_elevations = df["elevation_raw"].to_numpy()
    df["elevation"] = smooth_elevations(raw_elevations, window_size=smoothing_window)

    # Compute elevation deltas, gain, and loss
    ele_diffs = np.diff(df["elevation"].to_numpy(), prepend=df["elevation"].iloc[0])
    ele_gains = np.where(ele_diffs > 0, ele_diffs, 0.0)
    ele_losses = np.where(ele_diffs < 0, -ele_diffs, 0.0)

    df["ele_diff"] = ele_diffs
    df["ele_gain_delta"] = ele_gains
    df["ele_loss_delta"] = ele_losses
    df["cum_ele_gain"] = np.cumsum(ele_gains)
    df["cum_ele_loss"] = np.cumsum(ele_losses)

    # Calculate slope / gradient (%)
    dist_m = df["segment_dist_km"] * 1000.0
    df["gradient_pct"] = np.where(dist_m > 0, (df["ele_diff"] / dist_m) * 100.0, 0.0)

    total_distance = float(df["cum_dist_km"].iloc[-1])
    total_gain = float(df["cum_ele_gain"].iloc[-1])
    total_loss = float(df["cum_ele_loss"].iloc[-1])

    sectors = analyze_sectors(df)

    return TrackMetrics(
        total_distance_km=total_distance,
        total_elevation_gain_m=total_gain,
        total_elevation_loss_m=total_loss,
        min_elevation_m=float(df["elevation"].min()),
        max_elevation_m=float(df["elevation"].max()),
        points_df=df,
        sectors=sectors,
    )


def analyze_sectors(
    df: pd.DataFrame,
    boundaries: Optional[List[Tuple[str, float, float]]] = None,
) -> List[SectorProfile]:
    """
    Break down track into sectors and compute climbing density (m/km).
    Default boundaries align with SRMR key terrain changes:
    - Sector 1: 0 - 600 km (Front-loaded)
    - Sector 2: 600 - 1400 km (Rolling plateau & descents)
    - Sector 3: 1400 km - end (High mountain passes & hike-a-bike)
    """
    total_km = float(df["cum_dist_km"].iloc[-1])
    if boundaries is None:
        boundaries = [
            ("Sector 1 (Front-Loaded)", 0.0, min(600.0, total_km)),
            ("Sector 2 (Rolling Plateau)", min(600.0, total_km), min(1400.0, total_km)),
            ("Sector 3 (High Mountain Passes)", min(1400.0, total_km), total_km),
        ]

    sectors = []
    for name, start_k, end_k in boundaries:
        if start_k >= total_km:
            continue
        end_k_actual = min(end_k, total_km)
        sector_mask = (df["cum_dist_km"] >= start_k) & (df["cum_dist_km"] <= end_k_actual)
        sector_df = df[sector_mask]

        if len(sector_df) < 2:
            continue

        dist = end_k_actual - start_k
        if dist <= 0:
            continue

        gain = float(sector_df["ele_gain_delta"].sum())
        climbing_density = gain / dist
        avg_gradient = (gain / (dist * 1000.0)) * 100.0 if dist > 0 else 0.0

        sectors.append(
            SectorProfile(
                name=name,
                start_km=start_k,
                end_km=end_k_actual,
                distance_km=dist,
                elevation_gain_m=gain,
                climbing_density_m_per_km=climbing_density,
                avg_gradient_pct=avg_gradient,
            )
        )

    return sectors


def get_remaining_metrics(
    current_km: float, gpx_path: Optional[str] = None
) -> Tuple[float, float]:
    """
    Returns (remaining_distance_km, remaining_elevation_gain_m) given current_km position.
    If GPX file is provided and readable, uses exact GPX profile.
    Otherwise, uses baseline course parameters (2062 km, 36490 m gain).
    """
    if gpx_path and Path(gpx_path).exists():
        try:
            metrics = parse_gpx_file(gpx_path)
            df = metrics.points_df
            if current_km <= 0:
                return metrics.total_distance_km, metrics.total_elevation_gain_m
            elif current_km >= metrics.total_distance_km:
                return 0.0, 0.0

            idx = (df["cum_dist_km"] - current_km).abs().idxmin()
            current_cum_gain = float(df.loc[idx, "cum_ele_gain"])
            rem_dist = max(0.0, metrics.total_distance_km - current_km)
            rem_gain = max(0.0, metrics.total_elevation_gain_m - current_cum_gain)
            return rem_dist, rem_gain
        except Exception:
            pass

    if current_km <= 0.0:
        return DEFAULT_COURSE_DISTANCE_KM, DEFAULT_COURSE_ELEVATION_GAIN_M
    elif current_km >= DEFAULT_COURSE_DISTANCE_KM:
        return 0.0, 0.0

    rem_dist = max(0.0, DEFAULT_COURSE_DISTANCE_KM - current_km)

    completed_gain = 0.0
    if current_km <= 600.0:
        completed_gain = current_km * 15.0
    elif current_km <= 1400.0:
        completed_gain = (600.0 * 15.0) + (current_km - 600.0) * 10.5
    else:
        completed_gain = (600.0 * 15.0) + (800.0 * 10.5) + (current_km - 1400.0) * 28.73

    rem_gain = max(0.0, DEFAULT_COURSE_ELEVATION_GAIN_M - completed_gain)
    return rem_dist, rem_gain
