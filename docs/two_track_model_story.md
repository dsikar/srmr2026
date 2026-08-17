# The Two-Track Model: Decoupling Distance and Elevation in Ultra-Bikepacking

## Why Naive Extrapolation Fails

In ultra-endurance bikepacking events like the **Silk Road Mountain Race (SRMR)**, estimating finish time by simply taking elapsed distance and average speed ($T = D / v_{\text{avg}}$) leads to massive errors.

At Checkpoint 1 (51 hours elapsed, 657 km completed, +9,200 m elevation gain), a racer boasts a naive average speed of **12.88 km/h**. A linear extrapolation suggests a finish time of **160 hours (6 days, 16 hours)**.

However, this linear projection ignores the brutal reality of Kyrgyzstan's topography:
- **Sector 1 (0–600 km):** ~15.0 m/km climbing density
- **Sector 2 (600–1,400 km):** ~10.5 m/km climbing density (fast rolling plateau)
- **Sector 3 (1,400–2,062 km):** ~28.5–30.0 m/km climbing density (6 major passes peaking near 3,900 m with hike-a-bike)

Extrapolating current pace across the remaining 1,405 km assumes the rider will maintain rolling plateau speeds while hauling a bike over 27,000+ meters of vertical climbing at extreme altitudes.

---

## The Two-Track Model Formulation

To build an accurate, telemetry-free predictive model, we apply the classic **Naismith’s Rule / Minetti reductionist approach**—decoupling the route into horizontal work and vertical work.

Total race time $T$ is modeled as the sum of horizontal travel time and vertical climbing time:

$$T = T_{\text{distance}} + T_{\text{climb}} = \frac{D}{v_0} + \frac{H_{\text{gain}}}{VAM}$$

Where:
- $D$: Total course distance ($\text{km}$)
- $H_{\text{gain}}$: Total course elevation gain ($\text{m}$)
- $v_0$: Baseline rolling/flat speed ($\text{km/h}$)
- $VAM$: Vertical Ascent Meters per hour ($\text{m/h}$)

---

## Parameter Estimation from Current Data

Using the racer’s progress at the checkpoint:
- Distance covered ($d_1$): $657\text{ km}$
- Elevation gain covered ($h_1$): $\approx 9,200\text{ m}$
- Time elapsed ($t_1$): $51\text{ hours}$ (2 days, 3 hours)

$$\frac{657}{v_0} + \frac{9,200}{VAM} = 51\text{ hours}$$

In ultra-endurance unsupported bikepacking (including rest/stops and technical surface roll), a typical sustained all-day climbing rate is $VAM \approx 400\text{–}500\text{ m/h}$.

Solving for $v_0$ at $VAM = 450\text{ m/h}$:

$$T_{\text{climb, past}} = \frac{9,200\text{ m}}{450\text{ m/h}} \approx 20.44\text{ hours}$$

$$T_{\text{dist, past}} = 51 - 20.44 = 30.56\text{ hours} \implies v_0 = \frac{657\text{ km}}{30.56\text{ h}} \approx 21.5\text{ km/h}$$

---

## Full Course Projection ($D = 2,062\text{ km}$, $H_{\text{gain}} = 36,490\text{ m}$)

Using the calibrated pair ($v_0 \approx 21.5\text{ km/h}$, $VAM \approx 450\text{ m/h}$):

| Component | Calculation | Time |
| :--- | :--- | :---: |
| **Horizontal Track ($T_{\text{distance}}$)** | $2,062\text{ km} \div 21.5\text{ km/h}$ | **95.9 hours** |
| **Vertical Track ($T_{\text{climb}}$)** | $36,490\text{ m} \div 450\text{ m/h}$ | **81.1 hours** |
| **Total Estimated Race Time** | $95.9\text{ h} + 81.1\text{ h}$ | **177.0 hours** |

---

## Results & Model Comparison

- **Estimated Total Time:** $177\text{ hours}$ (~$7\text{ days, } 9\text{ hours}$)
- **Predicted Final Average Speed:** $11.65\text{ km/h}$ (down from current $12.88\text{ km/h}$)
- **Remaining Time from km 657:** $126\text{ hours}$ (~$5\text{ days, } 6\text{ hours}$)

This simple two-parameter model captures the heavy penalty of the upcoming $27,000\text{ m}+$ of vertical climbing without requiring complex machine learning models or live telemetry data.
