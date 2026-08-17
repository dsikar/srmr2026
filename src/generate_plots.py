"""
Script to generate high-resolution visualization plots for README.md.
Creates:
1. docs/assets/elevation_profile.png
2. docs/assets/model_comparison_projection.png
"""

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.gpx_parser import DEFAULT_COURSE_DISTANCE_KM, DEFAULT_COURSE_ELEVATION_GAIN_M, parse_gpx_file

GPX_PATH = "data/gpx/Silk_Road_Mountain_Race_2026.gpx"
ASSETS_DIR = Path("docs/assets")


def generate_all_plots():
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    # Load GPX if exists, otherwise create synthesized profile
    if Path(GPX_PATH).exists():
        metrics = parse_gpx_file(GPX_PATH)
        df = metrics.points_df
    else:
        # Fallback profile creation
        dists = np.linspace(0, DEFAULT_COURSE_DISTANCE_KM, 500)
        elevs = 1000 + 1000 * np.sin(dists / 100) + 1500 * (dists / DEFAULT_COURSE_DISTANCE_KM)
        df = pd.DataFrame({"cum_dist_km": dists, "elevation": elevs, "cum_ele_gain": np.linspace(0, DEFAULT_COURSE_ELEVATION_GAIN_M, 500)})

    # Plot 1: Elevation & Sector Profile
    fig, ax = plt.subplots(figsize=(12, 5), dpi=300)
    ax.plot(df["cum_dist_km"], df["elevation"], color="#1f77b4", linewidth=1.5, label="Elevation Profile (m)")
    ax.fill_between(df["cum_dist_km"], df["elevation"], color="#1f77b4", alpha=0.25)

    # Highlight Sectors
    sectors = [
        ("Sector 1: Front-Loaded\n(19.4 m/km)", 0, 600, "#2ca02c"),
        ("Sector 2: Rolling Plateau\n(13.6 m/km)", 600, 1400, "#ff7f0e"),
        ("Sector 3: Mountain Passes\n(19.3 m/km)", 1400, df["cum_dist_km"].iloc[-1], "#d62728"),
    ]

    for label, s_start, s_end, color in sectors:
        ax.axvspan(s_start, s_end, color=color, alpha=0.12)
        mid_km = (s_start + min(s_end, df["cum_dist_km"].iloc[-1])) / 2.0
        ax.text(mid_km, df["elevation"].max() * 0.92, label, ha="center", va="top", fontsize=9, fontweight="bold", color=color, bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=color, alpha=0.85))

    # Mark racer position at 657 km
    rider_km = 657.0
    idx = (df["cum_dist_km"] - rider_km).abs().idxmin()
    rider_ele = df.loc[idx, "elevation"]
    ax.plot(rider_km, rider_ele, marker="o", markersize=10, color="red", label="Racer Position @ CP1 (657 km)")
    ax.axvline(x=rider_km, color="red", linestyle="--", alpha=0.7)

    ax.set_title("Silk Road Mountain Race (SRMR 2026) - Terrain Profile & Rider Progress", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Distance (km)", fontsize=11)
    ax.set_ylabel("Elevation (m)", fontsize=11)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc="upper left", fontsize=10)
    plt.tight_layout()

    plot1_path = ASSETS_DIR / "elevation_profile.png"
    plt.savefig(plot1_path, dpi=300)
    plt.close()
    print(f"Generated: {plot1_path}")

    # Plot 2: Model Comparison & Time Projection Curve
    fig, ax = plt.subplots(figsize=(12, 5.5), dpi=300)

    # Distance points
    d_points = df["cum_dist_km"].to_numpy()
    e_points = df["cum_ele_gain"].to_numpy()

    # Naive Linear Model projection (v_avg = 657 / 51 = 12.882 km/h constant)
    v_naive = 657.0 / 51.0
    t_naive_curve = d_points / v_naive

    # Two-Track Decoupled Model curve (v_d = 21.5 km/h, v_h = 450 m/h)
    v_d = 21.5
    v_h = 450.0
    t_twotrack_curve = (d_points / v_d) + (e_points / v_h)

    ax.plot(d_points, t_naive_curve, label=f"Naive Linear Model (Const. {v_naive:.2f} km/h)", color="#d62728", linestyle="--", linewidth=2.0)
    ax.plot(d_points, t_twotrack_curve, label=f"Two-Track Model (v_d={v_d} km/h, VAM={v_h:.0f} m/h)", color="#2ca02c", linewidth=2.5)

    # Highlight CP1 checkpoint
    ax.plot(657, 51, marker="*", markersize=14, color="gold", markeredgecolor="black", label="Checkpoint 1 (51h, 657 km)")

    # Annotate final predicted finish times
    final_naive_h = t_naive_curve[-1]
    final_two_h = t_twotrack_curve[-1]

    ax.annotate(
        f"Naive Finish: {final_naive_h:.1f}h (6d 15h)",
        xy=(d_points[-1], final_naive_h),
        xytext=(d_points[-1] - 350, final_naive_h - 12),
        arrowprops=dict(arrowstyle="->", color="#d62728", lw=1.5),
        fontsize=9.5,
        fontweight="bold",
        color="#d62728",
    )

    ax.annotate(
        f"Two-Track Finish: {final_two_h:.1f}h (7d 9h)",
        xy=(d_points[-1], final_two_h),
        xytext=(d_points[-1] - 350, final_two_h + 10),
        arrowprops=dict(arrowstyle="->", color="#2ca02c", lw=1.5),
        fontsize=9.5,
        fontweight="bold",
        color="#2ca02c",
    )

    ax.set_title("SRMR 2026 Finish Projection: Naive Linear vs Two-Track Decoupled Model", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Distance (km)", fontsize=11)
    ax.set_ylabel("Elapsed Time (Hours)", fontsize=11)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc="upper left", fontsize=10)
    plt.tight_layout()

    plot2_path = ASSETS_DIR / "model_comparison_projection.png"
    plt.savefig(plot2_path, dpi=300)
    plt.close()
    print(f"Generated: {plot2_path}")


if __name__ == "__main__":
    generate_all_plots()
