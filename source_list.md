# Monitoring Sources

Selected for coverage of S2S prediction, compound/consecutive extremes, forecast verification, and ML/XAI for geoscience. Feeds verified 2026-03-13.

Review after 1-2 week pilot: drop feeds with zero relevant hits; add feeds if coverage gaps appear.

---

## Feeds (10)

### 1. Weather and Forecasting (AMS)
- **Feed:** `https://journals.ametsoc.org/action/showFeed?type=etoc&feed=rss&jc=waf`
- **Why:** Primary venue for S2S forecast verification, skill assessment, and operational prediction. Directly aligned with thesis core.
- **Expected noise:** Low. Most papers touch forecasting or verification.

### 2. Monthly Weather Review (AMS)
- **Feed:** `https://journals.ametsoc.org/action/showFeed?type=etoc&feed=rss&jc=mwre`
- **Why:** S2S model evaluation, ensemble methods, multi-model comparison, case studies of extreme event predictability.
- **Expected noise:** Low-moderate. Some synoptic-scale papers to filter.

### 3. Journal of Climate (AMS)
- **Feed:** `https://journals.ametsoc.org/action/showFeed?type=etoc&feed=rss&jc=jcli`
- **Why:** Teleconnections, climate variability, predictability sources (ENSO, MJO, NAO), compound extremes in climate context. Heavily represented in Zotero S2S Predictability collection.
- **Expected noise:** Moderate. Broad journal; abstract screening will filter palaeoclimate, ocean-only, etc.

### 4. Artificial Intelligence for the Earth Systems (AMS)
- **Feed:** `https://journals.ametsoc.org/action/showFeed?type=etoc&feed=rss&jc=aies`
- **Why:** ML and XAI applied to weather/climate prediction. Directly covers the thesis ML/XAI strand. Small journal, so very low volume and high signal.
- **Expected noise:** Very low. Nearly every paper is potentially relevant.

### 5. Hydrology and Earth System Sciences (Copernicus/EGU)
- **Feed:** `https://hess.copernicus.org/xml/rss2_0.xml`
- **Why:** Drought-flood transitions, hydrological whiplash, DFAA event identification, hazard indices (SPI, SRI, SWAP). Core venue for the flood-drought strand.
- **Expected noise:** Moderate. Groundwater, water quality, and catchment modelling papers to filter.

### 6. Natural Hazards and Earth System Sciences (Copernicus/EGU)
- **Feed:** `https://nhess.copernicus.org/xml/rss2_0.xml`
- **Why:** Compound hazards, multi-hazard risk, extreme event impacts. Covers the compound events framing of the thesis.
- **Expected noise:** Moderate. Seismic, landslide, and engineering-focused papers to filter.

### 7. Geophysical Research Letters (AGU/Wiley)
- **Feed:** `https://agupubs.onlinelibrary.wiley.com/feed/19448007/most-recent`
- **Why:** High-impact short papers across predictability, compound extremes, teleconnections, and ML applications. Barnes group XAI/forecasts-of-opportunity papers often appear here.
- **Expected noise:** High. Very broad journal; abstract screening essential.

### 8. Quarterly Journal of the Royal Meteorological Society (RMetS/Wiley)
- **Feed:** `https://rmets.onlinelibrary.wiley.com/feed/1477870X/most-recent`
- **Why:** Atmospheric dynamics and predictability theory, ensemble forecasting, ECMWF system evaluations, S2S skill diagnostics.
- **Expected noise:** Low-moderate. Focused on meteorology/atmospheric science.

### 9. Environmental Research Letters (IOP)
- **Feed:** `https://iopscience.iop.org/journal/rss/1748-9326`
- **Why:** Compound climate extremes, climate impacts, hydroclimatic variability. Publishes accessible synthesis and assessment papers relevant to thesis framing.
- **Expected noise:** Moderate. Broad environmental scope; energy, policy, and ecology papers to filter.

### 10. arXiv — Atmospheric and Oceanic Physics
- **Feed:** `https://export.arxiv.org/rss/physics.ao-ph`
- **Why:** Preprints on ML for weather/climate, data-driven S2S prediction, and new statistical methods. Catches papers weeks-months before journal publication.
- **Expected noise:** Moderate. Some ocean-only and NWP-only papers to filter.

---

## Considered but excluded

| Source | Reason for exclusion |
|---|---|
| arXiv physics.geo-ph | Content is predominantly seismology and solid-earth geophysics. Very low yield for S2S/hydroclimatic research. |
| Journal of Hydrology (Elsevier) | Many DFAA papers appear here, but Elsevier RSS access is unreliable. HESS covers the same niche with a working feed. Revisit if HESS misses key drought-flood papers. |
| npj Climate and Atmospheric Science (Nature) | Relevant but RSS returns redirect errors. Low volume journal so manual checking may suffice. Add if a working feed is found. |
| Earth's Future (AGU) | Compound events frameworks (Bevacqua, Zscheischler), but GRL already covers AGU high-impact papers. Add if compound event coverage proves thin. |
| Climate Dynamics (Springer) | Predictability and teleconnection papers, but broad and high-volume. JCLI and QJRMS cover the same niche. |
| BAMS (AMS) | Important for overview/perspective papers but publishes infrequently. Most relevant papers are editorials or reviews, not new research. |

---

## Notes

- Total feeds: 10 (within the 6-10 target range)
- **AMS feeds** are blocked by CloudFront bot protection (403). `screen.py` falls back to the Crossref API for these journals automatically (free, no auth, returns titles + abstracts)
- **Wiley feeds** use the ISSN-based `/feed/{issn}/most-recent` pattern (the `showFeed` URLs return 404 from scripts)
- **IOP feeds** use the `/journal/rss/{issn}` pattern
- **Copernicus** `/xml/rss2_0.xml` feeds work via direct HTTP fetch
- **arXiv** `export.arxiv.org` feeds work via direct HTTP fetch
- Volume estimate: ~50-150 new papers/week across all feeds combined; after abstract screening, expect ~2-10 relevant papers/week
