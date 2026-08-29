# ADR 0001: staged retrieval, pairwise LTR, and MMR

Status: accepted.

Run deterministic constraints before ML because user limits are contractual product intent. Blend popularity, content, and vector retrieval so their failure modes differ. Use a query-group-aware pairwise linear ranker: it is genuine LTR, interpretable, fast, and dependency-light; LambdaMART is the next production candidate after sufficient real labels. Weight pairs by inverse logged exposure propensity to reduce position bias, with clipping for variance control. Re-rank the short list with MMR over type and price to reduce near-duplicates. Exact local vector distance is reproducible; production substitutes a partitioned ANN index without changing the interface.

