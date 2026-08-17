# Task Objective: Front-Load Visual Plots and Narrative Model Story

## Instructions

1. **Generate & Front-Load Visual Plots**:
   - Create high-resolution plots illustrating:
     - Model comparison & finish time projection curve (Naive Linear vs Two-Track Decoupled).
     - Terrain profile with sector climbing density breakdown and racer position marker.
   - Save images in `docs/assets/` and embed them prominently at the top of `README.md`.

2. **Integrate Narrative Model Hook & Link**:
   - On `README.md`, provide a narrative hook explaining why linear extrapolation ($T = D / v_{\text{avg}}$) fails for SRMR due to back-loaded mountain pass topography.
   - Summarize the classic Naismith’s Rule / Minetti reductionist approach ($T = \frac{D}{v_0} + \frac{H_{\text{gain}}}{VAM}$).
   - Highlight the winner's predicted finish time ($177.0\text{ hours}$ / $7\text{d } 9\text{h}$, final average speed $11.65\text{ km/h}$).
   - Link to a dedicated narrative page: `docs/two_track_model_story.md`.

3. **Create Dedicated Narrative Document (`docs/two_track_model_story.md`)**:
   - Include full mathematical formulations, parameter estimation from current checkpoint data ($657\text{ km}$, $+9,200\text{ m}$, $51\text{ h}$ elapsed), solving for $v_0 = 21.5\text{ km/h}$ at $VAM = 450\text{ m/h}$.
   - Include full course projection table and comparison breakdown.

4. **Commit & Push**:
   - Ensure `.gitignore` allows tracking of `docs/assets/*.png`.
   - Stage all new plots, docs, prompts, and updated README.
   - Commit and push to the public GitHub repository.
