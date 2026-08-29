"""Download the official public-domain Maryland assessment export without scraping SDAT search."""
import argparse
from pathlib import Path
from urllib.request import urlretrieve

parser = argparse.ArgumentParser(); parser.add_argument("--url", required=True, help="Official opendata.maryland.gov CSV export URL")
parser.add_argument("--output", default="data/raw/maryland_assessments.csv")
args = parser.parse_args(); target = Path(args.output); target.parent.mkdir(parents=True, exist_ok=True)
urlretrieve(args.url, target); print(f"Downloaded {target} ({target.stat().st_size} bytes)")

