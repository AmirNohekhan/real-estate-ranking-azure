import argparse
import json
from pathlib import Path

from real_estate_ranking.data.pipeline import (
    generate_properties,
    simulate_listings,
    validate_properties,
    write_inventory,
)
from real_estate_ranking.simulation.behavior import generate_users, simulate_interactions

parser = argparse.ArgumentParser(); parser.add_argument("--mode", choices=["real", "sample", "synthetic"], default="sample")
args = parser.parse_args()
if args.mode == "real":
    raise SystemExit("Real download is intentionally separate: run scripts/download_public_data.py then map the official export. See docs/data_sources.md")
n = 2500 if args.mode == "sample" else 1000
props, report = validate_properties(generate_properties(n)); listings = simulate_listings(props); users = generate_users()
write_inventory(listings, Path("data/processed/listings.parquet")); write_inventory(users, Path("data/processed/users.parquet"))
events = simulate_interactions(users, listings); write_inventory(events, Path("data/processed/events.parquet"))
Path("reports").mkdir(exist_ok=True); Path("reports/data_quality.json").write_text(json.dumps(report.__dict__, indent=2))
print(json.dumps({"mode": args.mode, **report.__dict__, "events": len(events)}, indent=2))

