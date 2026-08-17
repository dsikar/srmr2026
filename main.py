"""
SRMR Race Tracker CLI Entrypoint.
Provides commands:
  - track: Parse GPX track and summarize course sectors & terrain density
  - checkpoint: Log a checkpoint and display comparative model predictions
  - summary: Show current race status and projections based on logged checkpoints
  - plot: Generate elevation profile visualization with rider position
"""

import json
from pathlib import Path
import re
from typing import Optional
import typer

from src.calibration import calibrate_coefficients
from src.gpx_parser import (
    DEFAULT_COURSE_DISTANCE_KM,
    DEFAULT_COURSE_ELEVATION_GAIN_M,
    get_remaining_metrics,
    parse_gpx_file,
)
from src.models import NaiveLinearModel, TwoTrackModel
from src.reporter import (
    generate_elevation_plot,
    print_checkpoint_projections,
    print_course_summary,
)

app = typer.Typer(help="SRMR 2026 Race Tracker CLI")

DEFAULT_GPX_PATH = "data/gpx/Silk_Road_Mountain_Race_2026.gpx"
CHECKPOINTS_FILE = "data/checkpoints.json"


def parse_time_string(time_str: str) -> float:
    """
    Parse time strings like '2d 3h', '51.0', '1d 12h 30m', '51h' into decimal hours.
    """
    time_str = time_str.strip().lower()
    try:
        return float(time_str)
    except ValueError:
        pass

    days = 0.0
    hours = 0.0
    minutes = 0.0

    d_match = re.search(r"(\d+(?:\.\d+)?)\s*d", time_str)
    h_match = re.search(r"(\d+(?:\.\d+)?)\s*h", time_str)
    m_match = re.search(r"(\d+(?:\.\d+)?)\s*m", time_str)

    if d_match:
        days = float(d_match.group(1))
    if h_match:
        hours = float(h_match.group(1))
    if m_match:
        minutes = float(m_match.group(1))

    total_hours = days * 24.0 + hours + (minutes / 60.0)
    if total_hours <= 0 and not (d_match or h_match or m_match):
        raise ValueError(f"Could not parse time string: '{time_str}'")
    return total_hours


def load_checkpoints() -> list:
    """Load logged checkpoints from JSON file."""
    path = Path(CHECKPOINTS_FILE)
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


def save_checkpoints(checkpoints: list) -> None:
    """Save checkpoints list to JSON file."""
    path = Path(CHECKPOINTS_FILE)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(checkpoints, f, indent=4)


@app.command()
def track(
    gpx: str = typer.Option(DEFAULT_GPX_PATH, "--gpx", "-g", help="Path to course GPX file")
):
    """
    Summarize course sectors, elevation profile, and climbing density.
    """
    if Path(gpx).exists():
        metrics = parse_gpx_file(gpx)
        print_course_summary(metrics)
    else:
        typer.echo(f"GPX file not found at {gpx}. Displaying default SRMR baseline course metrics.")
        # Fallback metric mock
        from src.gpx_parser import SectorProfile, TrackMetrics
        import pandas as pd
        sectors = [
            SectorProfile("Sector 1 (Front-Loaded)", 0.0, 600.0, 600.0, 9000.0, 15.0, 1.5),
            SectorProfile("Sector 2 (Rolling Plateau)", 600.0, 1400.0, 800.0, 8400.0, 10.5, 1.05),
            SectorProfile("Sector 3 (High Mountain Passes)", 1400.0, 2062.0, 662.0, 19090.0, 28.84, 2.88),
        ]
        df = pd.DataFrame({"cum_dist_km": [0, 2062], "elevation": [700, 3900]})
        metrics = TrackMetrics(2062.0, 36490.0, 36490.0, 700.0, 3900.0, df, sectors)
        print_course_summary(metrics)


@app.command()
def checkpoint(
    time: str = typer.Option(..., "--time", "-t", help="Elapsed time string (e.g. '2d 3h', '51')"),
    dist: float = typer.Option(..., "--dist", "-d", help="Elapsed distance in km"),
    ele: float = typer.Option(..., "--ele", "-e", help="Elapsed elevation gain in m"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Optional checkpoint description"),
    gpx: str = typer.Option(DEFAULT_GPX_PATH, "--gpx", "-g", help="Path to course GPX file"),
):
    """
    Log a new racer checkpoint and display updated projections comparing Naive vs Two-Track models.
    """
    elapsed_hours = parse_time_string(time)
    cps = load_checkpoints()
    new_id = len(cps) + 1

    cp_entry = {
        "id": new_id,
        "name": name or f"Checkpoint #{new_id}",
        "elapsed_hours": elapsed_hours,
        "distance_km": dist,
        "elevation_gain_m": ele,
        "timestamp_str": time,
    }

    # Avoid duplicating exact checkpoint
    if not any(c.get("elapsed_hours") == elapsed_hours and c.get("distance_km") == dist for c in cps):
        cps.append(cp_entry)
        save_checkpoints(cps)

    _evaluate_and_report(cp_entry, cps, gpx)


@app.command()
def summary(
    gpx: str = typer.Option(DEFAULT_GPX_PATH, "--gpx", "-g", help="Path to course GPX file")
):
    """
    Display current projections based on the latest logged checkpoint.
    """
    cps = load_checkpoints()
    if not cps:
        typer.echo("No checkpoints found. Adding baseline Day 2 + 3h checkpoint.")
        baseline = {
            "id": 1,
            "name": "CP1 Baseline (Day 2 + 3h)",
            "elapsed_hours": 51.0,
            "distance_km": 657.0,
            "elevation_gain_m": 9200.0,
            "timestamp_str": "Day 2 + 3h",
        }
        cps = [baseline]
        save_checkpoints(cps)

    latest_cp = cps[-1]
    _evaluate_and_report(latest_cp, cps, gpx)


@app.command()
def plot(
    gpx: str = typer.Option(DEFAULT_GPX_PATH, "--gpx", "-g", help="Path to course GPX file"),
    output: str = typer.Option("elevation_profile.png", "--output", "-o", help="Output PNG path"),
):
    """
    Generate elevation profile visualization with rider position.
    """
    cps = load_checkpoints()
    current_dist = cps[-1]["distance_km"] if cps else 0.0

    if Path(gpx).exists():
        metrics = parse_gpx_file(gpx)
        generate_elevation_plot(metrics, current_dist, output)
    else:
        typer.echo(f"GPX file not found at {gpx}. Cannot generate detailed plot.")


def _evaluate_and_report(latest_cp: dict, all_cps: list, gpx_path: str) -> None:
    # Check total distance and elevation gain from GPX if present
    if Path(gpx_path).exists():
        metrics = parse_gpx_file(gpx_path)
        total_dist = metrics.total_distance_km
        total_ele = metrics.total_elevation_gain_m
    else:
        total_dist = DEFAULT_COURSE_DISTANCE_KM
        total_ele = DEFAULT_COURSE_ELEVATION_GAIN_M

    # Remaining metrics
    rem_dist, rem_ele = get_remaining_metrics(latest_cp["distance_km"], gpx_path)

    # Calibrate coefficients
    calib = calibrate_coefficients(all_cps)

    # Models
    naive_model = NaiveLinearModel()
    twotrack_model = TwoTrackModel(v_d=calib.v_d, v_h=calib.v_h)

    naive_pred = naive_model.predict(
        elapsed_hours=latest_cp["elapsed_hours"],
        elapsed_dist_km=latest_cp["distance_km"],
        elapsed_ele_m=latest_cp["elevation_gain_m"],
        total_dist_km=total_dist,
        total_ele_m=total_ele,
    )

    twotrack_pred = twotrack_model.predict(
        elapsed_hours=latest_cp["elapsed_hours"],
        elapsed_dist_km=latest_cp["distance_km"],
        elapsed_ele_m=latest_cp["elevation_gain_m"],
        total_dist_km=total_dist,
        total_ele_m=total_ele,
        remaining_dist_km=rem_dist,
        remaining_ele_m=rem_ele,
    )

    print_checkpoint_projections(
        checkpoint_info=latest_cp,
        naive_pred=naive_pred,
        twotrack_pred=twotrack_pred,
        remaining_dist_km=rem_dist,
        remaining_ele_m=rem_ele,
        total_dist_km=total_dist,
        total_ele_m=total_ele,
    )


if __name__ == "__main__":
    app()
