# Data sources and provenance

Retrieved/verified 2026-08-29. This project does not redistribute a raw government export in Git.

## Maryland Real Property Assessments — Hidden Property Owner Names

- Provider: Maryland Department of Assessments and Taxation / Maryland Department of Planning
- Source: https://opendata.maryland.gov/Business-and-Economy/Maryland-Real-Property-Assessments-Hidden-Property/ed4q-f8tm
- Coverage: Maryland; real mode filters Montgomery County
- Variables intended: parcel/source ID, coordinates, premise geography, structure/use code, assessment, year built, building/land attributes when present
- License shown in official portal metadata: **Public Domain**
- Retrieval: official portal CSV/export endpoint or documented GIS download; never the interactive Real Property Data Search
- Transformation: schema mapping, owner fields excluded, county filter, normalization, validation, stable SHA-256 internal ID, Parquet
- Redistribution: raw export is not committed. Users must re-check current metadata and terms at retrieval time.

The interactive SDAT Real Property Data Search explicitly prohibits automated collection. It is therefore not an ingestion source. The open-data resource page identifies the statewide assessment dataset and official download route. Montgomery County open data additionally requires attribution/disclaimer for County-supplied datasets; this project includes the following when such enrichment is used:

> The data made available here has been modified for use from its original source, Montgomery County, Maryland. The County makes no representations or warranties as to completeness, accuracy, or timeliness. Use is at the user's own risk.

References: https://data.montgomerycountymd.gov/terms-of-use and https://codelibrary.amlegal.com/codes/montgomerycounty/latest/montgomeryco_md/0-0-0-118646.

## Field dictionary

| Field group | Provenance in real mode | Notes |
|---|---|---|
| source IDs, coordinates, jurisdiction, assessed value, supported structure fields | PUBLIC_SOURCE | exact mapping is versioned with acquired export |
| internal property ID, normalized type, calculated distance | DERIVED_PUBLIC | deterministic |
| listing ID/status/asking price/timestamp/DOM/price change/freshness | SIMULATED | not an active listing claim |
| user/session/search/event/device/experiment | SIMULATED | fictional marketplace behavior |
| retrieval/ranking scores and reason codes | MODEL_GENERATED | reason codes are product explanations, not SHAP |

