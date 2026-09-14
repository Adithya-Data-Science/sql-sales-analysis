import sqlite3
from pathlib import Path
from etl import run_etl

def test_multisource_etl_is_idempotent(tmp_path: Path):
    root = Path(__file__).parents[1]
    db = tmp_path / "integration.db"
    args = (root / "data/assets.csv", root / "data/usage.json", db)
    assert run_etl(*args) == (3, 4)
    assert run_etl(*args) == (3, 4)
    con = sqlite3.connect(db)
    try:
        assert con.execute("SELECT COUNT(*) FROM assets").fetchone()[0] == 3
        assert con.execute("SELECT COUNT(*) FROM asset_usage").fetchone()[0] == 4
        assert con.execute("SELECT SUM(hours) FROM asset_usage").fetchone()[0] == 20.0
    finally:
        con.close()
