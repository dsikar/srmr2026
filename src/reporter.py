"""
Reporter module for formatting CLI tables, printing race progress,
displaying model comparison predictions, and generating elevation profile plots.
"""

from typing import List, Optional
from src.gpx_parser import SectorProfile, TrackMetrics
from src.models import ModelPrediction

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


def print_course_summary(metrics: TrackMetrics, console: Optional[object] = None) -> None:
    """Print course breakdown and sector climbing density."""
    if RICH_AVAILABLE:
        con = console or Console()
        table = Table(title="SRMR 2026 - Course & Sector Terrain Profile", header_style="bold cyan")
        table.add_column("Sector", style="bold yellow")
        table.add_column("Range (km)", justify="right")
        table.add_column("Distance (km)", justify="right")
        table.add_column("Ele Gain (m)", justify="right")
        table.add_column("Climbing Density", justify="right", style="bold magenta")
        table.add_column("Avg Gradient", justify="right")

        for sector in metrics.sectors:
            table.add_row(
                sector.name,
                f"{sector.start_km:.0f} - {sector.end_km:.0f} km",
                f"{sector.distance_km:.1f} km",
                f"{sector.elevation_gain_m:,.0f} m",
                f"{sector.climbing_density_m_per_km:.1f} m/km",
                f"{sector.avg_gradient_pct:.2f} %",
            )

        con.print("\n")
        con.print(Panel(
            f"[bold green]Total Course Distance:[/bold green] {metrics.total_distance_km:,.1f} km\n"
            f"[bold green]Total Elevation Gain:[/bold green] {metrics.total_elevation_gain_m:,.0f} m\n"
            f"[bold green]Elevation Range:[/bold green] {metrics.min_elevation_m:.0f} m - {metrics.max_elevation_m:.0f} m",
            title="Course Baseline Specs",
            border_style="bright_blue",
        ))
        con.print(table)
    else:
        print("\n=== SRMR 2026 Course Overview ===")
        print(f"Total Distance: {metrics.total_distance_km:.1f} km")
        print(f"Total Elevation Gain: {metrics.total_elevation_gain_m:.0f} m")
        print("-" * 75)
        print(f"{'Sector':<30} {'Range':<15} {'Dist (km)':<10} {'Gain (m)':<10} {'Density (m/km)'}")
        print("-" * 75)
        for s in metrics.sectors:
            print(f"{s.name:<30} {s.start_km:.0f}-{s.end_km:.0f} km {s.distance_km:<10.1f} {s.elevation_gain_m:<10.0f} {s.climbing_density_m_per_km:.1f} m/km")
        print("-" * 75)


def print_checkpoint_projections(
    checkpoint_info: dict,
    naive_pred: ModelPrediction,
    twotrack_pred: ModelPrediction,
    remaining_dist_km: float,
    remaining_ele_m: float,
    total_dist_km: float,
    total_ele_m: float,
    console: Optional[object] = None,
) -> None:
    """Print comprehensive summary comparing Naive and Two-Track model predictions."""
    elapsed_h = checkpoint_info["elapsed_hours"]
    elapsed_d = checkpoint_info["distance_km"]
    elapsed_e = checkpoint_info["elevation_gain_m"]

    if RICH_AVAILABLE:
        con = console or Console()
        con.print("\n")
        
        # Current Status Panel
        status_text = (
            f"[bold white]Elapsed Time:[/bold white] {elapsed_h:.1f} hours ({naive_pred.days_hours_str.split(' ')[0]} + {elapsed_h % 24:.1f}h)\n"
            f"[bold white]Distance Covered:[/bold white] {elapsed_d:,.1f} / {total_dist_km:,.1f} km ({elapsed_d/total_dist_km*100:.1f}%)\n"
            f"[bold white]Elevation Completed:[/bold white] {elapsed_e:,.0f} / {total_ele_m:,.0f} m ({elapsed_e/total_ele_m*100:.1f}%)\n"
            f"[bold yellow]Remaining Distance:[/bold yellow] {remaining_dist_km:,.1f} km\n"
            f"[bold yellow]Remaining Elevation Gain:[/bold yellow] {remaining_ele_m:,.0f} m"
        )
        con.print(Panel(status_text, title=f"Racer Status @ Checkpoint ({checkpoint_info.get('name', 'Latest')})", border_style="cyan"))

        # Model Comparison Table
        table = Table(title="Model Projections & Pace Comparison", header_style="bold magenta")
        table.add_column("Metric", style="bold white")
        table.add_column("Naive Linear Model", justify="center", style="bold red")
        table.add_column("Two-Track Model (Decoupled)", justify="center", style="bold green")

        v_d_str = f"N/A (Uses v_avg={elapsed_d/elapsed_h:.2f} km/h)" if elapsed_h > 0 else "N/A"
        v_h_str = "N/A"
        if twotrack_pred.v_d is not None and twotrack_pred.v_h is not None:
            two_params = f"v_d = {twotrack_pred.v_d:.1f} km/h | v_h = {twotrack_pred.v_h:.0f} m/h"
        else:
            two_params = "N/A"

        table.add_row("Calibrated Parameters", v_d_str, two_params)
        table.add_row("Remaining Time", f"{naive_pred.remaining_hours:.1f} hours", f"{twotrack_pred.remaining_hours:.1f} hours")
        table.add_row("Predicted Total Hours", f"{naive_pred.total_hours:.1f} hours", f"{twotrack_pred.total_hours:.1f} hours")
        table.add_row("Projected Finish Time", naive_pred.days_hours_str, twotrack_pred.days_hours_str)
        table.add_row("Projected Final Avg Speed", f"{naive_pred.predicted_final_avg_speed_kmh:.2f} km/h", f"{twotrack_pred.predicted_final_avg_speed_kmh:.2f} km/h")

        con.print(table)
    else:
        print("\n=== RACER STATUS & PROJECTIONS ===")
        print(f"Elapsed Time: {elapsed_h:.1f} h")
        print(f"Distance: {elapsed_d:.1f} km / {total_dist_km:.1f} km")
        print(f"Elevation: {elapsed_e:.0f} m / {total_ele_m:.0f} m")
        print(f"Remaining: {remaining_dist_km:.1f} km | {remaining_ele_m:.0f} m gain")
        print("-" * 65)
        print(f"{'Metric':<25} {'Naive Linear':<20} {'Two-Track Model':<20}")
        print("-" * 65)
        print(f"{'Remaining Hours':<25} {naive_pred.remaining_hours:<20.1f} {twotrack_pred.remaining_hours:<20.1f}")
        print(f"{'Total Hours':<25} {naive_pred.total_hours:<20.1f} {twotrack_pred.total_hours:<20.1f}")
        print(f"{'Projected Finish':<25} {naive_pred.days_hours_str:<20} {twotrack_pred.days_hours_str:<20}")
        print(f"{'Final Avg Speed':<25} {naive_pred.predicted_final_avg_speed_kmh:<20.2f} {twotrack_pred.predicted_final_avg_speed_kmh:<20.2f}")
        print("-" * 65)


def generate_elevation_plot(
    metrics: TrackMetrics,
    current_dist_km: float,
    output_path: str = "elevation_profile.png",
) -> None:
    """Generate elevation profile plot with current rider position and sectors."""
    import matplotlib.pyplot as plt

    df = metrics.points_df
    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot elevation profile
    ax.plot(df["cum_dist_km"], df["elevation"], color="#1f77b4", linewidth=1.5, label="Elevation Profile")
    ax.fill_between(df["cum_dist_km"], df["elevation"], color="#1f77b4", alpha=0.2)

    # Mark current rider position
    if current_dist_km > 0:
        idx = (df["cum_dist_km"] - current_dist_km).abs().idxmin()
        curr_ele = df.loc[idx, "elevation"]
        ax.plot(current_dist_km, curr_ele, marker="o", markersize=10, color="red", label=f"Rider @ {current_dist_km:.0f} km")
        ax.axvline(x=current_dist_km, color="red", linestyle="--", alpha=0.7)

    # Highlight sectors
    colors = ["#2ca02c", "#ff7f0e", "#d62728"]
    for i, sector in enumerate(metrics.sectors):
        c = colors[i % len(colors)]
        ax.axvspan(sector.start_km, sector.end_km, color=c, alpha=0.1, label=f"{sector.name} ({sector.climbing_density_m_per_km:.1f} m/km)")

    ax.set_title("Silk Road Mountain Race (SRMR 2026) - Course Elevation & Sector Profile", fontsize=14, fontweight="bold")
    ax.set_xlabel("Distance (km)", fontsize=12)
    ax.set_ylabel("Elevation (m)", fontsize=12)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc="upper left", fontsize=10)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Elevation profile plot saved to: {output_path}")
