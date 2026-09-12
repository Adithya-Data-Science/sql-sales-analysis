from datetime import datetime, timezone

import sqlite3

from src.pipeline import (
    CoinbaseExchangeClient,
    SQLiteWarehouse,
    normalize_candles,
    split_time_windows,
    validate_candles,
)


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self, payloads):
        self.payloads = list(payloads)
        self.calls = []

    def get(self, url, params, timeout):
        self.calls.append({"url": url, "params": params, "timeout": timeout})
        return FakeResponse(self.payloads.pop(0))


def test_split_time_windows_respects_300_candle_limit():
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    end = datetime.fromtimestamp(start.timestamp() + 301 * 60, tz=timezone.utc)
    windows = list(split_time_windows(start, end, 60))
    assert len(windows) == 2
    assert int((windows[0][1] - windows[0][0]).total_seconds()) == 300 * 60


def test_api_client_calls_rest_endpoint_and_deduplicates_boundary():
    first = [
        [1000, "10", "15", "11", "14", "20"],
        [1060, "13", "16", "14", "15", "25"],
    ]
    second = [
        [1060, "13", "16", "14", "15", "25"],
        [1120, "14", "18", "15", "17", "30"],
    ]
    session = FakeSession([first, second])
    client = CoinbaseExchangeClient(base_url="https://api.example.test", session=session)

    start = datetime.fromtimestamp(0, tz=timezone.utc)
    end = datetime.fromtimestamp(301 * 60, tz=timezone.utc)
    candles = client.get_product_candles("BTC-USD", start, end, 60)

    assert len(session.calls) == 2
    assert session.calls[0]["url"].endswith("/products/BTC-USD/candles")
    assert [c.timestamp for c in candles] == [1000, 1060, 1120]


def test_validation_rejects_inconsistent_high_low():
    candles = normalize_candles("BTC-USD", [[1000, "12", "13", "11", "14", "1"]])
    try:
        validate_candles(candles)
        assert False, "expected validation error"
    except ValueError as exc:
        assert "High price" in str(exc) or "Low price" in str(exc)


def test_sqlite_upsert_is_idempotent(tmp_path):
    db = tmp_path / "market.db"
    warehouse = SQLiteWarehouse(db)
    warehouse.initialize()
    candles = normalize_candles(
        "BTC-USD",
        [
            [1000, "10", "15", "11", "14", "20"],
            [1060, "13", "16", "14", "15", "25"],
        ],
    )
    validate_candles(candles)
    warehouse.upsert(candles)
    warehouse.upsert(candles)

    with sqlite3.connect(db) as conn:
        count = conn.execute("SELECT COUNT(*) FROM candles").fetchone()[0]
    assert count == 2
    assert warehouse.summary("BTC-USD")["candle_count"] == 2
