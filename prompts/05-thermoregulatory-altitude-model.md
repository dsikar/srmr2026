# Task Directive: Thermoregulatory & Altitude Temperature Coupling Model

**System Role & Task Directive:**
You are an expert computational modeling agent specializing in physiological energetics and network flow dynamics (using our established Kirchhoff/Maxwell circuit-analogy framework). Your objective is to expand the existing model to integrate **altitude-dependent ambient temperature**, **dynamic thermoregulatory energy expenditure**, and their **feedback impact on moving speed** (focusing strictly on external environmental factors, excluding hydration/dehydration).

---

### Context & Baseline

* We have completed **two days of empirical tracking data** (distance, altitude profile, elapsed time, pacing, and energy expenditure).
* Treat the route as an impedance/network model where physical terrain and environmental stress represent resistive/potential nodes.

---

### Implementation Instructions

#### 1. Environmental Temperature Field
* Define ambient temperature $T(h)$ as a continuous function of altitude $h$:
* Baseline boundary values: $T(h_{\min}) = 40^\circ\text{C}$ (lowest altitude $933\text{ m}$) down to $T(h_{\max}) = 0^\circ\text{C}$ (highest altitude $3,918\text{ m}$).
* Implement an environmental lapse rate:

$$T(h) = T_{\text{base}} - \Gamma \cdot (h - h_{\min})$$

*(Calibrate $\Gamma \approx 0.0134^\circ\text{C/m}$ to match the 40°C $\to$ 0°C transition across the route's elevation range).*

#### 2. Thermoregulation Energy Cost Function
* Model metabolic thermoregulation cost per unit time ($P_{\text{thermo}}$) relative to a physiological thermoneutral zone ($T_{\text{neutral}} \approx 18^\circ\text{C}\text{--}22^\circ\text{C}$):
* **Heat dissipation overhead ($T > T_{\text{upper}} = 22^\circ\text{C}$):** Cost of sweating, peripheral vasodilation, and cardiovascular strain approaching 40°C.
* **Cold defense overhead ($T < T_{\text{lower}} = 18^\circ\text{C}$):** Cost of shivering/non-shivering thermogenesis and peripheral vasoconstriction approaching 0°C.

$$E_{\text{thermo}} = \int P_{\text{thermo}}(T(h(s)), v(s)) \, dt = \int \frac{P_{\text{thermo}}(T(h(s)), v(s))}{v(s)} \, ds$$

#### 3. Energy Accounting & Debt Tracking (Kirchhoff Analog)
* **Sunk Energy Cost ($E_{\text{paid}}$):** Ingest the 2-day historical data to compute the cumulative energy already paid for thermoregulation and mechanical work up to Checkpoint 1 (657 km, 51h).
* **Projected Remaining Cost ($E_{\text{remaining}}$):** Integrate projected thermoregulatory demand over the remaining distance and elevation profile.
* Map this into our Kirchhoff-style energy budget: treat total available metabolic energy as a potential source with internal dissipation losses.

#### 4. Speed & Pacing Adjustment
* Calculate the reduction in available mechanical power:

$$P_{\text{mechanical}}(t) = P_{\text{total\_available}} - P_{\text{thermo}}(t)$$

* Derive the adjusted target average speed $v(s)$ across remaining segments based on available mechanical output and thermal strain thresholds.
* Compare the revised model predictions against the empirical average speeds from Days 1 and 2 to validate calibration.

---

### Output Requirements

1. Mathematical formulation of $T(h)$, $P_{\text{thermo}}$, and the power-velocity coupling.
2. A dedicated documentation page (`docs/thermoregulatory_altitude_model.md`).
3. An updated budget table showing: **Paid Cost (Days 1–2)**, **Remaining Projected Cost**, and **Net Adjusted Average Speed**.
4. Analysis highlighting which segment carries the highest combined thermal-mechanical penalty.
5. Add subheader `Roadmap` and link on `README.md`.
6. Commit and push code with author **Antigravity**.
