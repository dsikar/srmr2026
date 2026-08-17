# SRMR 2026 Race Tracker & Predictive Pace Model

A modular Python framework for real-time race tracking, predictive time estimation, and terrain modeling tailored to the **Silk Road Mountain Race (SRMR 2026)**.

---

## 1. External Resources & Links

- **Official Race Website:** [Silk Road Mountain Race 2026](https://www.themountainraces.cc/srmr2026)
- **Live Dot Watching:** [SRMR 2026 MAProgress Tracking](https://srmr2026.maprogress.com/)
- **Official Podcast:** [The Mountain Races Podcast on Spotify](https://open.spotify.com/show/36v8Hy0VofuPnfapp8ZOD1)
- **Course GPX Route Source:** [RideWithGPS Route #53318000](https://ridewithgps.com/routes/53318000)

---

## 2. Background & Mathematical Model

The Silk Road Mountain Race is an ultra-endurance bikepacking race across Kyrgyzstan:
- **Total Course Distance:** 2,062 km
- **Total Elevation Gain:** +36,490 m

A naive linear extrapolation ($T = D / v_{\text{avg}}$) fails because the course topography is heavily front/back-loaded:
- **0–600 km:** ~15.0 m/km climbing density
- **600–1,400 km:** ~10.5 m/km climbing density (faster rolling plateau and descents)
- **1,400–2,062 km:** ~28.5–30.0 m/km climbing density (6 major passes peaking near 3,900 m with hike-a-bike)

### The Two-Track Model

We decouple horizontal rolling work from vertical elevation ascent (Naismith / Minetti principle):

$$T_{\text{total}} = T_{\text{distance}} + T_{\text{elevation}} = \frac{D}{v_d} + \frac{H_{\text{gain}}}{v_h}$$

Where:
- $D$: Course distance (km)
- $H_{\text{gain}}$: Cumulative elevation gain (m)
- $v_d$: Distance rate / rolling velocity (km/h) [Calibrated: $21.5\text{ km/h}$]
- $v_h$: Elevation rate / Vertical Ascent Meters per hour (VAM) [Calibrated: $450\text{ m/h}$]

### Baseline Calibration
- **Default Baseline Projection:** $177.0\text{ hours}$ (7 days, 9 hours)
- **Projected Final Average Speed:** $11.65\text{ km/h}$

---

## 3. Codebase Architecture

```
srmr2026/
├── data/
│   ├── gpx/
│   │   └── Silk_Road_Mountain_Race_2026.gpx   # Official course GPX track
│   └── checkpoints.json                       # Racer checkpoint history
│
├── src/
│   ├── __init__.py
│   ├── gpx_parser.py                          # GPX parsing, elevation smoothing & sector analysis
│   ├── models.py                              # NaiveLinearModel & TwoTrackModel implementations
│   ├── calibration.py                         # Bounded least-squares regression for (v_d, v_h)
│   └── reporter.py                            # Rich CLI tables & Matplotlib elevation plotter
│
├── tests/
│   ├── test_gpx_parser.py                     # Parser unit tests
│   └── test_models.py                         # Model & calibration unit tests
│
├── prompts/
│   ├── 01-smrs2026-analysis.md
│   └── 02-readme-and-github.md
│
├── main.py                                    # Typer CLI entrypoint
├── requirements.txt                           # Package dependencies
└── README.md
```

---

## 4. Installation & Quickstart

### Environment Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 5. CLI Usage Commands

### 1. Summarize Course Terrain & Sectors
```bash
python main.py track --gpx data/gpx/Silk_Road_Mountain_Race_2026.gpx
```

### 2. Log Checkpoint & Compare Models
```bash
python main.py checkpoint --time "2d 3h" --dist 657 --ele 9200
```
Outputs a comparison table between the **Naive Linear Model** and the **Two-Track Decoupled Model**.

### 3. Display Current Race Status Summary
```bash
python main.py summary
```

### 4. Generate Elevation Profile Plot
```bash
python main.py plot --output elevation_profile.png
```

---

## 6. Running Tests

```bash
pytest -v
```
