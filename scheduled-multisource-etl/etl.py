from __future__ import annotations
import argparse, csv, json, logging, sqlite3
from datetime import datetime, timezone
from pathlib import Path

LOG = logging.getLogger("scheduled_etl")

def load_assets(path: Path):
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    required = {"asset_id", "asset_name", "department"}
    if not rows or required - set(rows[0]):
        raise ValueError("Invalid asset CSV schema")
    return rows

def load_usage(path: Path):
    rows = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(rows, list) or not rows:
        raise ValueError("Usage JSON must be a non-empty list")
    for r in rows:
        if not {"asset_id", "usage_date", "hours"} <= set(r):
            raise ValueError("Invalid usage JSON schema")
        if float(r["hours"]) < 0:
            raise ValueError("Negative usage hours")
    return rows

def run_etl(assets_path: Path, usage_path: Path, db_path: Path):
    assets = load_assets(assets_path)
    usage = load_usage(usage_path)
    ids = {r["asset_id"] for r in assets}
    unknown = sorted({r["asset_id"] for r in usage} - ids)
    if unknown:
        raise ValueError(f"Unknown asset IDs: {unknown}")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(db_path)
    try:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS assets (
          asset_id TEXT PRIMARY KEY, asset_name TEXT NOT NULL, department TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS asset_usage (
          asset_id TEXT NOT NULL, usage_date TEXT NOT NULL, hours REAL NOT NULL CHECK(hours >= 0),
          loaded_at TEXT NOT NULL,
          PRIMARY KEY(asset_id, usage_date),
          FOREIGN KEY(asset_id) REFERENCES assets(asset_id)
        );
        """)
        con.executemany(
            "INSERT INTO assets VALUES(?,?,?) ON CONFLICT(asset_id) DO UPDATE SET asset_name=excluded.asset_name, department=excluded.department",
            [(r["asset_id"], r["asset_name"], r["department"]) for r in assets]
        )
        loaded_at = datetime.now(timezone.utc).isoformat()
        con.executemany(
            "INSERT INTO asset_usage VALUES(?,?,?,?) ON CONFLICT(asset_id,usage_date) DO UPDATE SET hours=excluded.hours, loaded_at=excluded.loaded_at",
            [(r["asset_id"], r["usage_date"], float(r["hours"]), loaded_at) for r in usage]
        )
        con.commit()
        return len(assets), len(usage)
    finally:
        con.close()

def main():
    p = argparse.ArgumentParser(description="Schedule-ready multi-source ETL integration")
    p.add_argument("--assets", default="data/assets.csv")
    p.add_argument("--usage", default="data/usage.json")
    p.add_argument("--db", default="data/integration.db")
    p.add_argument("--log", default="data/etl.log")
    a = p.parse_args()
    Path(a.log).parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(filename=a.log, level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    n_assets, n_usage = run_etl(Path(a.assets), Path(a.usage), Path(a.db))
    LOG.info("ETL success assets=%s usage_rows=%s", n_assets, n_usage)
    print(f"ETL success: assets={n_assets}, usage_rows={n_usage}, db={a.db}")

if __name__ == "__main__":
    main()
