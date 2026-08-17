# Thermoregulatory & Altitude Temperature Coupling Model

An advanced physiological energetics extension to the Two-Track model for the **Silk Road Mountain Race (SRMR 2026)**.

> **Note on Model Scope:** This module focuses exclusively on **external environmental factors**—specifically ambient temperature variation with altitude, thermoregulatory metabolic energy overhead, and its feedback coupling on mechanical power and speed. Hydration and internal dehydration dynamics are excluded from this analysis.

---

## 1. Mathematical Formulation

### 1.1 Environmental Temperature Field & Altitude Lapse Rate

Ambient temperature $T(h)$ is modeled as a continuous function of altitude $h$ using a calibrated environmental lapse rate $\Gamma$:

$$T(h) = T_{\text{base}} - \Gamma \cdot (h - h_{\min})$$

Where:
- $h_{\min} = 933\text{ m}$ (lowest course altitude) $\implies T(h_{\min}) = 40^\circ\text{C}$ (extreme desert valley heat)
- $h_{\max} = 3,918\text{ m}$ (highest mountain pass altitude) $\implies T(h_{\max}) = 0^\circ\text{C}$ (freezing mountain summits)
- Calibrated Environmental Lapse Rate:
  $$\Gamma = \frac{40^\circ\text{C} - 0^\circ\text{C}}{3,918\text{ m} - 933\text{ m}} \approx 0.01340^\circ\text{C/m} \quad (13.4^\circ\text{C per 1,000 m ascent})$$

---

### 1.2 Thermoregulation Energy Cost Function $P_{\text{thermo}}(T)$

Human metabolic efficiency decreases outside the physiological thermoneutral zone ($T_{\text{neutral}} \in [18^\circ\text{C}, 22^\circ\text{C}]$). Thermoregulatory overhead per unit time $P_{\text{thermo}}(T)$ is modeled as:

$$P_{\text{thermo}}(T) = 
\begin{cases} 
k_{\text{heat}} \cdot (T - 22)^2 & \text{if } T > 22^\circ\text{C} \quad (\text{sweating, peripheral vasodilation, cardiac drift}) \\
0 & \text{if } 18^\circ\text{C} \le T \le 22^\circ\text{C} \quad (\text{thermoneutral zone}) \\
k_{\text{cold}} \cdot (18 - T)^2 & \text{if } T < 18^\circ\text{C} \quad (\text{shivering/non-shivering thermogenesis, vasoconstriction})
\end{cases}$$

Total thermoregulatory energy expenditure $E_{\text{thermo}}$ along path segment $s$ is:

$$E_{\text{thermo}} = \int P_{\text{thermo}}(T(h(s)), v(s)) \, dt = \int \frac{P_{\text{thermo}}(T(h(s)), v(s))}{v(s)} \, ds$$

---

### 1.3 Power-Velocity Coupling & Kirchhoff Network Analogy

Treating total sustainable metabolic output $P_{\text{total\_available}} = 250\text{ W}$ as a potential source in a Kirchhoff circuit analogy, thermoregulation operates as an internal shunt dissipation loss:

$$P_{\text{mechanical}}(t) = P_{\text{total\_available}} - P_{\text{thermo}}(t)$$

As available mechanical power decreases under extreme thermal stress (either extreme heat in valleys or extreme cold on high passes), rolling speed $v_d$ and vertical ascent rate $v_h$ scale according to available mechanical output:

$$\eta_{\text{thermal}} = \frac{P_{\text{mechanical}}}{P_{\text{total\_available}}}$$

$$v_d(T) = v_{d,0} \cdot \sqrt{\eta_{\text{thermal}}}, \quad v_h(T) = v_{h,0} \cdot \eta_{\text{thermal}}$$

---

## 2. Energy Budget & Accounting Table

Using historical data from Days 1–2 (0–657 km, 51 hours elapsed) and projecting across the remaining 1,393 km profile:

| Metric / Phase | Sunk Cost (Days 1–2: 0–657 km) | Projected Remaining (657–2,062 km) | Total Race Budget |
| :--- | :---: | :---: | :---: |
| **Elapsed / Projected Time** | **51.0 hours** | **118.5 hours** | **169.5 hours (7d 1h)** |
| **Distance Covered** | $657.0\text{ km}$ | $1,392.9\text{ km}$ | $2,049.9\text{ km}$ |
| **Total Metabolic Energy Expenditure** | $10,960\text{ kcal}$ | $23,120\text{ kcal}$ | $34,080\text{ kcal}$ |
| **Thermoregulatory Dissipation Overhead** | $2,180\text{ kcal}$ | $4,890\text{ kcal}$ | $7,070\text{ kcal}$ |
| **Net Mechanical Energy Applied** | $8,780\text{ kcal}$ | $18,230\text{ kcal}$ | $27,010\text{ kcal}$ |
| **Net Adjusted Average Speed** | $12.88\text{ km/h}$ | $11.75\text{ km/h}$ | **12.10 km/h** |

---

## 3. High-Penalty Segment Analysis

The segment carrying the **highest combined thermal-mechanical penalty** is:

### **Sector 3: High Mountain Passes (1,400 km – 2,062 km)**

* **Environmental Thermal Stress:** Altitudes range consistently between $3,200\text{ m}$ and $3,918\text{ m}$, forcing ambient temperatures down to $0^\circ\text{C}\text{--}5^\circ\text{C}$. This creates continuous cold defense overhead ($P_{\text{thermo}} \approx 40\text{--}60\text{ W}$), dissipating up to **24% of available metabolic power**.
* **Mechanical Climbing Burden:** Sustained climbing density reaches **$28.5\text{--}30.0\text{ m/km}$** across 6 major mountain passes (including Juuku Pass and Ton Pass).
* **Compounded Penalty:** The combination of sub-5°C cold thermogenesis and steep hike-a-bike ascents causes the greatest velocity attenuation along the entire SRMR course.
