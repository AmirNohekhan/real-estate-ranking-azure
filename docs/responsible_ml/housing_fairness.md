# Responsible housing ML

The ranker includes price and physical home characteristics, explicit query geography, distance, listing freshness, content similarity, and non-demographic interaction history. It excludes race, color, religion, sex, disability, familial status, national origin, and any inferred analogues. Census demographics, school ratings, crime scores, names, and free-text neighborhood stereotypes are intentionally absent.

Geography and price can still act as proxies and encode historic inequity. Explicit geography is honored as user intent but is not inferred from protected traits. Monitoring should compare exposure, rank quality, error, and catalog coverage across legally reviewed geographic slices; a qualified fair-housing/legal review must approve any production feature or audit design. Do not optimize for engagement alone: position and selection bias can produce rich-get-richer feedback loops.

Mitigations include hard-query transparency, propensity logging, exploration, coverage/diversity monitoring, time-based evaluation, feature review, drift alarms, appeal/report channels, and human governance. MMR diversification is a product-quality tool, not proof of legal fairness. Synthetic behavior cannot validate real-world fairness or consumer outcomes.

