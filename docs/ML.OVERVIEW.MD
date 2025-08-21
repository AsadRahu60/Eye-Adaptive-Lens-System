# Machine Learning Overview

**Goal:** use a simple, safe ML layer to *suggest* small therapy adjustments
(e.g., occlusion duty), while **hard safety limits** always dominate.

## What exists now
- Synthetic data generator → `data/sessions/synth_training.csv`
- Trainer → Logistic Regression saved to `models/therapy_lr.joblib`
- Inference policy → `ml_suggest()` with safety clamps + comfort guard
- Fallback → rule-based if model missing or confidence low

## Feature schema (per row)
- `dist_cm`, `lux`, `head_yaw`
- `prev_duty`, `prev_defocus_dpt`
- `comfort_0_10`
- Label for training: `task_success` in `{0,1}`

## Safety guardrails
- Max duty = 0.5; min = 0.0; step = 0.05
- Max |defocus| = 0.50 D; step = 0.10 D
- Only increase challenge if `p_improve ≥ 0.70` **and** `comfort ≥ 6.0`
- Else decrease or hold; **firmware still enforces bounds**

## Roadmap
- Replace synthetic with real session logs
- Add per-user models; A/B compare against rule-based baseline
- Log model version + inputs for auditability

### Last updated: 2025-08-17

