from __future__ import annotations
import argparse, csv, sqlite3
from pathlib import Path

CUSTOMER_COLS = {"customer_id", "customer_name", "state"}
ORDER_COLS = {"order_id", "customer_id", "order_date", "amount", "status"}
VALID_STATUS = {"completed", "pending", "cancelled"}

def read_csv(path: Path, required: set[str]) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"No rows in {path}")
    missing = required - set(rows[0])
    if missing:
        raise ValueError(f"Missing columns {sorted(missing)} in {path}")
    return rows

def validate(customers, orders):
    customer_ids = [r["customer_id"] for r in customers]
    if len(customer_ids) != len(set(customer_ids)):
        raise ValueError("Duplicate customer_id")
    order_ids = [r["order_id"] for r in orders]
    if len(order_ids) != len(set(order_ids)):
        raise ValueError("Duplicate order_id")
    known = set(customer_ids)
    for r in orders:
        if r["customer_id"] not in known:
            raise ValueError(f"Unknown customer_id {r['customer_id']}")
        if float(r["amount"]) < 0:
            raise ValueError("Negative amount")
        if r["status"] not in VALID_STATUS:
            raise ValueError(f"Invalid status {r['status']}")

def build_warehouse(db_path: Path, customers_path: Path, orders_path: Path) -> None:
    customers = read_csv(customers_path, CUSTOMER_COLS)
    orders = read_csv(orders_path, ORDER_COLS)
    validate(customers, orders)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(db_path)
    try:
        con.executescript("""
        DROP TABLE IF EXISTS fact_orders;
        DROP TABLE IF EXISTS dim_customers;
        CREATE TABLE dim_customers (
          customer_key INTEGER PRIMARY KEY AUTOINCREMENT,
          customer_id TEXT UNIQUE NOT NULL,
          customer_name TEXT NOT NULL,
          state TEXT NOT NULL
        );
        CREATE TABLE fact_orders (
          order_id TEXT PRIMARY KEY,
          customer_key INTEGER NOT NULL,
          order_date TEXT NOT NULL,
          amount REAL NOT NULL CHECK(amount >= 0),
          status TEXT NOT NULL,
          FOREIGN KEY(customer_key) REFERENCES dim_customers(customer_key)
        );
        """)
        con.executemany(
            "INSERT INTO dim_customers(customer_id, customer_name, state) VALUES (?, ?, ?)",
            [(r["customer_id"], r["customer_name"], r["state"]) for r in customers],
        )
        key_map = dict(con.execute("SELECT customer_id, customer_key FROM dim_customers"))
        con.executemany(
            "INSERT INTO fact_orders(order_id, customer_key, order_date, amount, status) VALUES (?, ?, ?, ?, ?)",
            [(r["order_id"], key_map[r["customer_id"]], r["order_date"], float(r["amount"]), r["status"]) for r in orders],
        )
        con.commit()
        failures = con.execute("""
          SELECT COUNT(*) FROM fact_orders f
          LEFT JOIN dim_customers c ON f.customer_key = c.customer_key
          WHERE c.customer_key IS NULL OR f.amount < 0 OR f.order_id IS NULL
        """).fetchone()[0]
        if failures:
            raise RuntimeError(f"Warehouse quality checks failed: {failures}")
    finally:
        con.close()

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--customers", default="data/customers.csv")
    p.add_argument("--orders", default="data/orders.csv")
    p.add_argument("--db", default="data/warehouse.db")
    a = p.parse_args()
    build_warehouse(Path(a.db), Path(a.customers), Path(a.orders))
    print(f"Warehouse built: {a.db}")

if __name__ == "__main__":
    main()
