# Task Directive: Remove Kirchhoff Analogy and Fix LaTeX Math Syntax Rendering

## Instructions

1. **Remove Kirchhoff Analogy References**:
   - Remove all mentions of "Kirchhoff", "Maxwell", "circuit analogy", "network flow dynamics", and "resistive nodes" from `README.md`, `docs/thermoregulatory_altitude_model.md`, `src/thermo_model.py`, and `prompts/05-thermoregulatory-altitude-model.md`.
   - Keep the physiological model simple and direct (focusing on ambient temperature lapse rate $T(h)$, thermoregulatory metabolic power overhead $P_{\text{thermo}}(T)$, and available mechanical power $P_{\text{mechanical}} = P_{\text{total}} - P_{\text{thermo}}$).

2. **Fix KaTeX / LaTeX Math Rendering Errors**:
   - Fix all LaTeX math blocks in `docs/thermoregulatory_altitude_model.md` and `README.md` where underscores caused KaTeX rendering failures (e.g. replace `P_{\text{total\_available}}` with `P_{\text{total}}` or `P_{\text{avail}}`).
   - Ensure clean, valid LaTeX math syntax throughout all markdown files.

3. **Commit & Push to Remote**:
   - Run test suite (`pytest -v`).
   - Commit changes with author signed as **Antigravity**.
   - Push to remote GitHub repository (`dsikar/srmr2026`).
