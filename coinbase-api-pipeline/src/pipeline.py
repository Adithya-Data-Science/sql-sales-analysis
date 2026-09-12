from __future__ import annotations

import argparse
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Iterator, Sequence

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

ALLOWED_GRANULARITIES = {60, 300, 900, 3600, 21600, 86400}
MAX_CANDLES_PER_REQUEST = 300
DEFAULT_BASE_URL = "https://api.exchange.coinbase.com"


@dataclass(frozen=True)
class Candle:
    product_id: str
    timestamp: int
    low: float
    high: float
    open: float
    close: float
    volume: float


def _to_utc_datetime(value: str) -> datetime:
    text = value.strip().replace("Z", "+00:00")
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _to_rfc3339(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def split_time_windows(start: datetime, end: datetime, granularity: int) -> Iterator[tuple[datetime, datetime]]:
    if granularity not in ALLOWED_GRANULARITIES:
        raise ValueError(f"Unsupported granularity: {granularity}")
    if start >= end:
        raise ValueError("start must be before end")

    window_seconds = granularity * MAX_CANDLES_PER_REQUEST
    cursor = int(start.timestamp())
    final = int(end.timestamp())
    while cursor < final:
        window_end = min(cursor + window_seconds, final)
        yield (
            datetime.fromtimestamp(cursor, tz=timezone.utc),
            datetime.fromtimestamp(window_end, tz=timezone.utc),
        )
        cursor = window_end


class CoinbaseExchangeClient:
    def __init__(self, base_url: str = DEFAULT_BASE_URL, timeout: int = 15, session=None) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session or self._build_session()

    @staticmethod
    def _build_session() -> requests.Session:
        retry = Retry(
            total=4,
            connect=4,
            read=4,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset({"GET"}),
            respect_retry_after_header=True,
        )
        session = requests.Session()
        session.headers.update({"User-Agent": "portfolio-coinbase-api-pipeline/1.0"})
        session.mount("https://", HTTPAdapter(max_retries=retry))
        return session

    def get_product_candles(
        self,
        product_id: str,
        start: datetime,
        end: datetime,
        granularity: int,
    ) -> list[Candle]:
        rows: list[Sequence[object]] = []
        for window_start, window_end in split_time_windows(start, end, granularity):
            response = self.session.get(
                f"{self.base_url}/products/{product_id}/candles",
                params={
                    "start": _to_rfc3339(window_start),
                    "end": _to_rfc3339(window_end),
                    "granularity": granularity,
                },
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, list):
                raise ValueError("Expected a list response from Coinbase candles endpoint")
            rows.extend(payload)

        candles = normalize_candles(product_id, rows)
        deduplicated = {c.timestamp: c for c in candles}
        result = sorted(deduplicated.values(), key=lambda c: c.timestamp)
        validate_candles(result)
        return result


def normalize_candles(product_id: str, rows: Iterable[Sequence[object]]) -> list[Candle]:
    candles: list[Candle] = []
    for row in rows:
        if len(row) < 6:
            raise ValueError(f"Malformed candle row: {row}")
        candles.append(
            Candle(
                product_id=product_id,
                timestamp=int(row[0]),
                low=float(row[1]),
                high=float(row[2]),
                open=float(row[3]),
                close=float(row[4]),
                volume=float(row[5]),
            )
        )
    return candles


def validate_candles(candles: Sequence[Candle]) -> None:
    seen: set[int] = set()
    for candle in candles:
        if candle.timestamp in seen:
            raise ValueError(f"Duplicate timestamp: {candle.timestamp}")
        seen.add(candle.timestamp)
        if candle.low < 0 or candle.high < 0 or candle.open < 0 or candle.close < 0:
            raise ValueError("Price fields must be non-negative")
        if candle.volume < 0:
            raise ValueError("Volume must be non-negative")
        if candle.low > min(candle.open, candle.close, candle.high):
            raise ValueError(f"Low price is inconsistent at {candle.timestamp}")
        if candle.high < max(candle.open, candle.close, candle.low):
            raise ValueError(f"High price is inconsistent at {candle.timestamp}")


class SQLiteWarehouse:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def initialize(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS candles (
                    product_id TEXT NOT NULL,
                    timestamp INTEGER NOT NULL,
                    low REAL NOT NULL,
                    high REAL NOT NULL,
                    open REAL NOT NULL,
                    close REAL NOT NULL,
                    volume REAL NOT NULL,
                    ingested_at TEXT NOT NULL,
                    PRIMARY KEY (product_id, timestamp)
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_candles_timestamp ON candles(timestamp)")

    def upsert(self, candles: Sequence[Candle]) -> int:
        if not candles:
            return 0
        ingested_at = datetime.now(timezone.utc).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.executemany(
                """
                INSERT INTO candles (
                    product_id, timestamp, low, high, open, close, volume, ingested_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(product_id, timestamp) DO UPDATE SET
                    low=excluded.low,
                    high=excluded.high,
                    open=excluded.open,
                    close=excluded.close,
                    volume=excluded.volume,
                    ingested_at=excluded.ingested_at
                """,
                [
                    (
                        c.product_id,
                        c.timestamp,
                        c.low,
                        c.high,
                        c.open,
                        c.close,
                        c.volume,
                        ingested_at,
                    )
                    for c in candles
                ],
            )
        return len(candles)

    def summary(self, product_id: str) -> dict[str, object]:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                """
                SELECT
                    COUNT(*) AS candle_count,
                    MIN(timestamp) AS first_timestamp,
                    MAX(timestamp) AS last_timestamp,
                    ROUND(AVG(close), 4) AS avg_close,
                    ROUND(SUM(volume), 4) AS total_volume,
                    ROUND(MIN(low), 4) AS min_low,
                    ROUND(MAX(high), 4) AS max_high
                FROM candles
                WHERE product_id = ?
                """,
                (product_id,),
            ).fetchone()
        keys = ["candle_count", "first_timestamp", "last_timestamp", "avg_close", "total_volume", "min_low", "max_high"]
        return dict(zip(keys, row, strict=True))


def run_pipeline(product_id: str, start: datetime, end: datetime, granularity: int, db_path: str | Path) -> dict[str, object]:
    client = CoinbaseExchangeClient()
    candles = client.get_product_candles(product_id, start, end, granularity)
    warehouse = SQLiteWarehouse(db_path)
    warehouse.initialize()
    rows_written = warehouse.upsert(candles)
    return {"rows_written": rows_written, "warehouse_summary": warehouse.summary(product_id)}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ingest Coinbase public candle data into SQLite")
    parser.add_argument("--product", default="BTC-USD", help="Coinbase product ID, e.g. BTC-USD")
    parser.add_argument("--start", required=True, help="UTC/RFC3339 start time")
    parser.add_argument("--end", required=True, help="UTC/RFC3339 end time")
    parser.add_argument("--granularity", type=int, default=3600, choices=sorted(ALLOWED_GRANULARITIES))
    parser.add_argument("--db", default="data/market_data.db", help="SQLite output path")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = run_pipeline(
        product_id=args.product,
        start=_to_utc_datetime(args.start),
        end=_to_utc_datetime(args.end),
        granularity=args.granularity,
        db_path=args.db,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
