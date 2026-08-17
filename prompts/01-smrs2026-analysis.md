# Objective
Create a modular Python repository for real-time race tracking, predictive time estimation, and terrain modeling for ultra-endurance bikepacking events, specifically tailored to the Silk Road Mountain Race (SRMR).

---

## 1. Background & Context
We are tracking a racer in a fixed-course ultra-endurance cycling race:
- **Total Course Distance:** 2,062 km
- **Total Elevation Gain:** +36,490 m
- **Baseline Checkpoint (Day 2 + 3 hours / 51 hours elapsed):**
  - Distance Covered: 657 km
  - Elevation Gain Completed: ~9,200 m
  - Current Naive Average Speed: 12.88 km/h

A naive linear extrapolation based solely on distance ($T = D / v_{\text{avg}}$) fails because the course topography is severely front/back-loaded:
- **0–600 km:** ~15.0 m/km climbing density
- **600–1,400 km:** ~10.5 m/km climbing density (faster rolling plateau and long descents)
- **1,400–2,062 km:** ~28.5–30.0 m/km climbing density (6 major passes peaking near 3,900 m with hike-a-bike sections)

---

## 2. Core Mathematical Model (The Two-Track Model)
To keep the model interpretable and free of unavailable telemetry (e.g., heart rate, power), implement the decoupled horizontal/vertical work formulation (Naismith / Minetti reductionist principle):

$$T_{\text{total}} = T_{\text{distance}} + T_{\text{elevation}} = \frac{D}{v_d} + \frac{H_{\text{gain}}}{v_h}$$

Where:
- $D$: Total course distance (km)
- $H_{\text{gain}}$: Total cumulative elevation gain (m)
- $v_d$: Distance rate / rolling velocity (km/h)
- $v_h$: Elevation rate / Vertical Ascent Meters per hour (VAM in m/h)

### Initial Calibrated Coefficients:
- $v_d = 21.5\text{ km/h}$
- $v_h = 450\text{ m/h}$
- **Current Baseline Projection:** $177.0\text{ hours}$ (7 days, 9 hours) $\rightarrow$ Projected Final Average Speed: $11.65\text{ km/h}$.

---

## 3. Required Repository Architecture

Build a clean Python project with the following structure:


```

srmr-race-tracker/
│
├── data/
│   ├── gpx/                  # Directory for course GPX tracks
│   └── checkpoints.json      # Log of historical racer checkpoints (time, dist, ele)
│
├── src/
│   ├── **init**.py
│   ├── gpx_parser.py         # Extracts cumulative distance, elevation gain/loss, and slope profiles
│   ├── models.py             # Implements NaiveLinearModel and TwoTrackModel
│   ├── calibration.py        # Optimizes/fits (v_d, v_h) from series of checkpoints
│   └── reporter.py           # Formats CLI tables and projections
│
├── tests/
│   ├── test_gpx_parser.py
│   └── test_models.py
│
├── main.py                   # CLI entrypoint to add checkpoints and run projections
├── requirements.txt          # gpxpy, pandas, scipy, matplotlib, typer/argparse, rich
└── README.md

```

---

## 4. Key Implementation Details

### `src/gpx_parser.py`
- Parse `.gpx` tracks using `gpxpy`.
- Calculate haversine distance between sequential points.
- Apply a small elevation smoothing filter (rolling mean or Butterworth) to avoid GPS elevation noise.
- Provide a helper function `get_remaining_metrics(current_km)` that returns `(remaining_distance_km, remaining_elevation_gain_m)`.

### `src/models.py`
- **`NaiveLinearModel`**: Extrapolates $T = D \times (t_{\text{elapsed}} / d_{\text{elapsed}})$.
- **`TwoTrackModel`**:
  - Accepts parameters $v_d$ (km/h) and $v_h$ (m/h).
  - Calculates remaining time based on upcoming segment profile: 
    $$t_{\text{remaining}} = \frac{D_{\text{remaining}}}{v_d} + \frac{H_{\text{remaining}}}{v_h}$$
  - Returns total time, predicted finish ETA, and predicted final average speed.

### `src/calibration.py`
- Given $N \ge 1$ checkpoint records $[(t_1, d_1, h_1), (t_2, d_2, h_2), \dots]$, solve for optimal $(v_d, v_h)$ using bounded least-squares regression (`scipy.optimize.minimize`), with physiologically bounded ranges ($15 \le v_d \le 30\text{ km/h}$, $250 \le v_h \le 650\text{ m/h}$).

### `main.py` (CLI Interface)
Provide CLI commands using `argparse` or `typer`:
1. `python main.py track --gpx data/course.gpx` $\rightarrow$ Summarize course sectors and climbing density.
2. `python main.py checkpoint --time "2d 3h" --dist 657 --ele 9200` $\rightarrow$ Log a new checkpoint and display updated projections comparing Naive vs. Two-Track models.
3. `python main.py plot` $\rightarrow$ Optional: Generate an elevation profile showing current rider position and projected sector paces.

---

## 5. Output Deliverables
1. Full, working source code with unit tests.
2. `checkpoints.json` seeded with the Day 2 + 3h checkpoint ($d=657\text{ km}, h=9200\text{ m}, t=51.0\text{ h}$).
3. A formatted terminal summary table using `rich` or standard ASCII formatting displaying:
   - Elapsed vs. Remaining metrics
   - Parameter values ($v_d, v_h$)
   - Model comparisons (Total hours, Days/Hours, Final Avg Speed)


