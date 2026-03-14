# Relevance Rules

Instructions for scoring papers during screening. Apply to title + abstract only.

---

## Scoring scale

| Score | Label | Definition |
|-------|-------|------------|
| 0 | Irrelevant | No connection to S2S prediction, compound/consecutive extremes, forecast verification, or ML/XAI for geoscience. Falls under an exclusion topic. |
| 1 | Tangential | Touches a relevant domain (e.g. drought, climate variability) but does not address S2S timescales, prediction skill, event compounding, or verification. |
| 2 | Possibly useful | Addresses a relevant topic but only peripherally to the thesis — e.g. S2S prediction of a single variable with no compound/event framing, or ML for weather at non-S2S timescales. May be useful as background. |
| 3 | Relevant | Directly addresses at least one thesis strand with clear methodological or conceptual overlap. Worth reading. |
| 4 | Highly relevant | Addresses the thesis core question or bridges two or more thesis strands. Likely to inform a chapter, method, or research gap argument. Priority read. |

**Save threshold: score >= 3.** Papers scoring 0-2 are discarded.

---

## Score 4 triggers (any one is sufficient)

- S2S prediction or verification of compound, consecutive, or sequential extremes
- Drought-flood transitions, DFAA, or hydrological/precipitation whiplash at S2S timescales
- Event-based (not variable-based) S2S predictability assessment
- Forecast skill conditioned on large-scale atmospheric state for multi-hazard events
- XAI or interpretable ML diagnosing when/why S2S forecast skill emerges
- New verification methods designed for temporally compounding hazards
- Window-based event definitions aligned to forecast lead times

## Score 3 triggers (any one is sufficient)

- S2S forecast skill assessment (any variable, any region)
- Compound or consecutive hydroclimatic extremes (identification, drivers, or indices)
- Sources of S2S predictability (MJO, ENSO, NAO, IOD, SSW, land-atmosphere)
- Windows of opportunity or forecasts of opportunity at subseasonal timescales
- ML or hybrid ML-dynamical methods applied to S2S prediction or postprocessing
- XAI methods (SHAP, saliency, LRP) applied to any geoscience prediction problem
- Forecast verification methodology relevant to S2S (proper scoring rules, extreme event metrics, ensemble verification)
- Hazard indices for drought, flood, or transitions (SPI, SPEI, SRI, SWAP, MSDFI, DFAA indices) with a prediction or verification component
- Multi-model ensembling for S2S

## Automatic exclusions (score 0, do not evaluate further)

- Pure climate projections (CMIP/SSP) with no forecast skill component
- Synoptic NWP (days 1-5) with no S2S connection
- Ocean-only or sea-ice-only prediction
- Remote sensing methodology only
- Air quality, pollution, urban heat island
- Palaeoclimate reconstruction
- Semantic segmentation, computer vision unrelated to weather/climate
- Energy/market forecasting not evaluating S2S inputs

---

## Scoring procedure

1. Check exclusions first — if any match, assign 0 and stop.
2. Check timescale — if the paper is exclusively weather-scale (days 1-5) or decadal+, assign 0.
3. Check score-4 triggers — if any match, assign 4.
4. Check score-3 triggers — if any match, assign 3.
5. Otherwise, judge whether the paper is tangential (1) or possibly useful (2) based on proximity to the include topics in research_scope.md.

## Output fields per saved paper

| Field | Description |
|-------|-------------|
| date | Date screened |
| title | Paper title |
| source | Feed / journal name |
| link | URL to paper |
| relevance_score | 3 or 4 |
| relevance_summary | 1-2 sentence reason for the score |
| topic_labels | Comma-separated labels from: `s2s-prediction`, `compound-extremes`, `drought-flood`, `verification`, `predictability-sources`, `teleconnections`, `ml-s2s`, `xai`, `hazard-indices`, `ensemble-methods`, `event-definition` |
