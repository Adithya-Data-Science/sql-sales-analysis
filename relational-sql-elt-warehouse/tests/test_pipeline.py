import sqlite3
from pathlib import Path
from pipeline import build_warehouse

def test_end_to_end(tmp_path: Path):
    root = Path(__file__).parents[1]
    db = tmp_path / "warehouse.db"
    build_warehouse(db, root / "data/customers.csv", root / "data/orders.csv")
    con = sqlite3.connect(db)
    try:
        assert con.execute("SELECT COUNT(*) FROM dim_customers").fetchone()[0] == 3
        assert con.execute("SELECT COUNT(*) FROM fact_orders").fetchone()[0] == 4
        assert con.execute("SELECT ROUND(SUM(amount),2) FROM fact_orders WHERE status='completed'").fetchone()[0] == 3730.5
    finally:
        con.close()
