# Measured Feedback Tipping Points: Did the Policy Work, or Just Look Like It?

Repository: [github.com/balakumar-v/feedback-tipping-points](https://github.com/balakumar-v/feedback-tipping-points)

Balakumar V (leader) · Kishore Kumar J · K Asvitha

> **Bottom line.** Old logs can't see repeat fatigue, so a new ranking policy can look good in logs and still lose clicks after launch. Our audit measures fatigue with a small randomized slice and returns **APPROVE**, **REJECT** or **NEED RANDOMIZED DATA**. In a preliminary simulator test, logs showed +0.084 where the true ten-round lift was −0.019, and the audit approved none of 144 worse cases while the one-step gate approved all 144.

## 1. Problem & Theme Chosen

**Theme 2, Problem 3.** A recommender team must decide whether to launch a new ranking policy from historical logs. Logs may show a short-term lift (change in click rate) that repeated exposure erodes later, so a wrong launch loses clicks once live. One randomized slice can screen many candidates; an A/B test answers one.

## 2. Understanding of the Challenge

One-step **OPE** needs **overlap**, **known propensities** and **no hidden confounder**. It misses fatigue (click odds fall with each repeat) from repeats a new policy creates, and **hidden taste** can inflate logs-only estimates.

## 3. Proposed Approach

The audit has five steps; **bold** terms are in the glossary.

1. **Data.** The simulator gives counterfactual ground truth; the Open Bandit Dataset (OBD, public store click logs) gives logged clicks and display propensities.
2. **One-step estimate.** **IPW, SNIPS, DM and cross-fitted DR** estimate one-step lift; **effective sample size** is reported.
3. **Fatigue slice.** A 3,000-user, ten-round randomized slice repeats the previous item half the time; user-level bootstraps quantify uncertainty.
4. **Fatigue shapes.** Four **shapes** and a free-form curve (one free value per repeat count) forecast each policy's ten-round lift and estimate κ̂ (**fatigue strength**). The tipping point κ\* is the fatigue strength at which forecast lift reaches zero; it is reported, never a gate.
5. **Verdict.** The verdict engine applies one rule:
   - **APPROVE** needs *all four* shapes to show a forecast lift with lower 95% bound above zero, the free-form curve to agree, and the **coverage guard** to pass.
   - **REJECT** needs all four to agree on a loss.
   - Otherwise: **NEED RANDOMIZED DATA**, with n\* reported as a hint only.

Logs-only audits never approve because hidden taste is untestable.

**Planned:** APPROVE must also hold under the fitted **logit attenuation**, κ̂ × √(1 + 0.346 γ²), at γ = 1.6; effective sample size below 10% of users forces NEED.

## 4. Minimum Viable Scope

The MVP is the verdict engine (`python -m p3ope audit`): logs and a randomized slice in, a verdict with κ̂, κ\* and n\* out.

**Working now:**

- The engine, its tests and the live demo on our simulator;
- On full OBD, DR is about 9% below the A/B click rate and its interval misses it;
- Drift check: before/after gets the sign wrong in all 200 runs after a uniform click-odds drop.

**Midway report target, 1 Dec:** attenuation gate integrated, 200-world grid scored and OBD loader running; KuaiRand is optional.

## 5. Stretch Ambitions

KuaiRand (public short-video logs with random insertions): estimate κ̂ on real repeats and run the Section 7 placebo on its real rounds.

## 6. Novelty / Differentiation

The new part is the audit itself. It measures repeat fatigue with a small randomized slice instead of assuming it, forecasts lift under four fatigue shapes plus a free-form curve, and answers NEED RANDOMIZED DATA when evidence is thin. Approval needs all four shapes to agree, and the coverage guard blocks it if over 5% of showings exceed the slice's repeat range. We build on non-stationary OPE (Chandak et al.) and fatigue models (Levine et al.).

**Claim to test:** At matched correct-approval rates, the audit falsely approves fewer worse policies than the listed baselines and delivers greater net value.

**Costs:** Uniform serving loses about a quarter of OBD clicks; if n\* exceeds our 8,000-user cap, run a real A/B.

## 7. Evaluation Plan

**Metrics:** false approval (a worse policy approved) with a one-sided 95% bound; false reject; correct approve; net value per audit at λ = 1, 5, 10 (an approval earns the true lift, or loses λ times its harm if worse), shown beside an oracle that approves exactly the better policies.

**Baselines:** Before/after; one-step OPE gate; best single shape; equal-exposure A/B; non-stationary OPE forecast (Chandak et al.).

**Real-data placebo:** Randomly assign repeat counts to OBD clicks. Assigned repeats have no causal effect by construction, so κ̂'s interval should cover zero in at least 95% of reshuffles.

**Pre-registered targets** (rule frozen before we wrote the test generators; we report failure if missed):

| Measure | Target |
| --- | --- |
| False-approval bound | ≤ 5% |
| False approval, near-boundary (true lift within 0.01 of zero) | ≤ 10% |
| False reject | ≤ 10% |
| Correct approve | ≥ 25% |
| Placebo coverage | ≥ 95% |

**Results so far (simulator, preliminary):** On a held-out generator the audit approved none of 144 worse cases (one-step gate: all 144) and correctly approved 26 of 48 better cases. Single shapes falsely approved up to 6 of 36; four-shape agreement approved none. A second, structurally different generator (40 worlds) produced no false approvals.

**Where we miss our targets:** Cases share only 9 **worlds**, so the by-world false-approval bound is 28% (13% across both generators) against 5%, and the n\* band covered the truth in 85% of pilot runs against 90%. We plan to fix both in the next stage with a sealed 200-world grid (about 60 worse worlds; 59 clean would bound false approval at 5%) and a no-fatigue world where the audit must approve.

**Limits:** Fatigue is validated only on our own simulators, so some success is built in; fatigue is assumed uniform across users; intervals used 30 bootstrap resamples so far (200 for final verdicts).

## 8. Feasibility & Risks

**Team**

- **Balakumar V** (leader): simulation, bootstrap inference and estimators; built a hybrid-search RAG chatbot.
- **Kishore Kumar J**: pipelines and loaders; his assistive app, where false alerts cost, parallels false approvals.
- **K Asvitha**: experiment design and live-audit demo; built an agent that reproduces bugs from vague reports.

**Timeline**

- **10–16 Nov:** OBD loader and 200-world grid.
- **17–23 Nov:** attenuation-aware gate.
- **24–30 Nov:** KuaiRand mapping; go/no-go by 30 Nov, with OBD and the simulator as fallback; **midway report 1 Dec**.
- **2–6 Dec:** A/B and non-stationary baselines, net-value table, placebo and ablations.
- **Buffer through 14 Dec;** drop KuaiRand first.

**Risks**

1. Hidden taste may attenuate measured fatigue, risking false approval. Randomization removes exposure confounding, but attenuation remains; until the gate lands (23 Nov), APPROVE assumes taste is within the tested range.
2. KuaiRand may lack suitable repeat-exposure data.

## Glossary

| Term | Definition |
| --- | --- |
| OPE | Off-policy evaluation: estimating a new policy's results from old logs. |
| Overlap | Logs cover what the new policy would show. |
| Known propensities | Logged display probabilities. |
| No hidden confounder | No unlogged factor drives both display and click. |
| Hidden taste | Unlogged preference behind both display and click. |
| IPW, SNIPS, DM, DR | Standard one-step estimators: propensity-weighted, self-normalized, direct model, doubly robust. |
| Effective sample size | How many logged users really count. |
| Shapes | Linear, logarithmic, 0.7-discounted recency, steeper after two repeats. |
| Fatigue strength (κ̂) | Estimated fall in click log-odds per repeat. |
| n\* | Slice size for 80% power to exclude zero lift. |
| Coverage guard | Blocks approval when over 5% of the new policy's showings exceed the slice's repeat range. |
| Logit attenuation | Adjustment for hidden taste weakening measured fatigue; 0.346 fitted. |
| Case, world | A world is one simulated policy pair with its fatigue mechanism; a case is one audit of it. Cases in one world are not independent. |