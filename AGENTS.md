# AGENTS.md — AI Agent Operating Briefing & Directives

This document provides operational guidelines, code conventions, environment setup commands, and architecture references for AI agents working in the **SRMR 2026 Race Tracker** repository.

---

## 1. Project Overview & Scope

- **Repository:** `dsikar/srmr2026`
- **Objective:** Real-time race tracking, terrain modeling, and predictive time estimation for the Silk Road Mountain Race (SRMR 2026) in Kyrgyzstan (2,062 km, +36,490 m elevation gain).
- **Core Models:**
  1. **Two-Track Model:** Decoupled horizontal rolling work and vertical climbing ascent ($T = \frac{D}{v_0} + \frac{H_{\text{gain}}}{VAM}$). Calibrated baseline: $v_0 = 21.5\text{ km/h}, VAM = 450\text{ m/h} \implies 177.0\text{ hours}$ total time.
  2. **Thermoregulatory & Altitude Model:** Altitude-dependent ambient temperature lapse rate $T(h)$, metabolic thermoregulation power overhead $P_{\text{thermo}}(T)$, and mechanical power output coupling $P_{\text{mech}} = P_{\text{total}} - P_{\text{thermo}}(T)$.
- **Scope Constraint:** Focus strictly on **external environmental factors**. Do **NOT** add hydration or internal dehydration dynamics.

---

## 2. Core Directives & Rules for AI Agents

1. **Python Indentation:** Strictly use **4 spaces** for indentation in all Python code files.
2. **Verification & Testing:** Always run `.venv/bin/pytest -v` after modifying code files to verify 100% test pass status before completing tasks.
3. **Markdown & Math Syntax:** Ensure clean KaTeX / LaTeX math formatting in markdown docs. Avoid unescaped `_` or invalid `\_` inside math mode blocks (`$...$` or `$$...$$`).
4. **Git Commit Authoring:** Sign all git commits with author `Antigravity <antigravity@google.com>`.
5. **Git Asset Tracking:** Visual plots in `docs/assets/*.png` must remain tracked by Git for rendering on GitHub.

---

## 3. Environment & Execution Commands

```bash
# Virtual environment setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run full test suite (12 unit tests)
.venv/bin/pytest -v

# Run CLI track summary
.venv/bin/python main.py track --gpx data/gpx/Silk_Road_Mountain_Race_2026.gpx

# Log checkpoint and compare model projections
.venv/bin/python main.py checkpoint --time "2d 3h" --dist 657 --ele 9200

# View current race status summary
.venv/bin/python main.py summary

# Re-generate visualization plots
.venv/bin/python src/generate_plots.py
```

---

## 4. Repository Structure & Module Responsibilities

```
srmr2026/
├── AGENTS.md                                  # AI agent operational briefing & directives
├── README.md                                  # Human-facing project overview & roadmap
├── main.py                                    # CLI entrypoint (Typer commands)
├── requirements.txt                           # Package dependencies
│
├── data/
│   ├── gpx/Silk_Road_Mountain_Race_2026.gpx   # Official course GPX track
│   └── checkpoints.json                       # Log of racer checkpoint records
│
├── docs/
│   ├── assets/
│   │   ├── elevation_profile.png              # Terrain profile & rider position plot
│   │   └── model_comparison_projection.png   # Naive vs Two-Track finish curve
│   ├── two_track_model_story.md               # Full mathematical narrative doc
│   └── thermoregulatory_altitude_model.md     # Thermoregulatory & altitude model doc
│
├── src/
│   ├── __init__.py                            # Package init
│   ├── gpx_parser.py                          # GPX parsing, haversine, elevation smoothing, sector analysis
│   ├── models.py                              # NaiveLinearModel & TwoTrackModel implementations
│   ├── calibration.py                         # Bounded least-squares regression for (v_d, v_h)
│   ├── thermo_model.py                        # Altitude temperature lapse rate & thermoregulatory overhead
│   ├── generate_plots.py                      # Matplotlib plot generator
│   └── reporter.py                            # Rich CLI tables & terminal formatting
│
├── tests/
│   ├── test_gpx_parser.py                     # Parser unit tests
│   ├── test_models.py                         # Model unit tests
│   └── test_thermo_model.py                   # Thermo model unit tests
│
└── prompts/                                   # Task directives log
    ├── 01-smrs2026-analysis.md
    ├── 02-readme-and-github.md
    ├── 03-frontload-eye-candy-and-model-story.md
    ├── 04-add-josh-ibbett-youtube.md
    ├── 05-thermoregulatory-altitude-model.md
    └── 06-remove-kirchhoff-and-fix-latex.md
```

---

## 5. Chronological Prompt Directives Log

1. [`prompts/01-smrs2026-analysis.md`](file:///home/daniel/Documents/cycling/srmr2026/prompts/01-smrs2026-analysis.md) — Initial objective & Two-Track model specification.
2. [`prompts/02-readme-and-github.md`](file:///home/daniel/Documents/cycling/srmr2026/prompts/02-readme-and-github.md) — README overview & GitHub repo creation.
3. [`prompts/03-frontload-eye-candy-and-model-story.md`](file:///home/daniel/Documents/cycling/srmr2026/prompts/03-frontload-eye-candy-and-model-story.md) — Front-load visual plots & narrative story document.
4. [`prompts/04-add-josh-ibbett-youtube.md`](file:///home/daniel/Documents/cycling/srmr2026/prompts/04-add-josh-ibbett-youtube.md) — Add Josh Ibbett's YouTube channel link.
5. [`prompts/05-thermoregulatory-altitude-model.md`](file:///home/daniel/Documents/cycling/srmr2026/prompts/05-thermoregulatory-altitude-model.md) — Thermoregulatory metabolic power overhead & altitude temperature lapse rate.
6. [`prompts/06-remove-kirchhoff-and-fix-latex.md`](file:///home/daniel/Documents/cycling/srmr2026/prompts/06-remove-kirchhoff-and-fix-latex.md) — Kirchhoff removal & KaTeX syntax fix.
