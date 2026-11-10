import pytest
import pandas as pd

from cleaner.config import load_config
from cleaner.steps import (normalize_headers, clean_strings, clean_numeric,
                           parse_dates, map_values, dedupe, handle_missing)


def test_normalize_headers():
    df = pd.DataFrame(columns=["Customer Name ", "SIGNUP DATE", "Amount ($)"])
    out = normalize_headers(df)
    assert list(out.columns) == ["customer_name", "signup_date", "amount"]


def test_clean_strings_trims_and_nulls_blanks():
    df = pd.DataFrame({"name": ["  Ravi   Kumar ", "   ", "Amit"]})
    out = clean_strings(df)
    assert out["name"].iloc[0] == "Ravi Kumar"
    assert pd.isna(out["name"].iloc[1])
    assert out["name"].iloc[2] == "Amit"


def test_clean_numeric_strips_symbols_and_counts_failures():
    df = pd.DataFrame({"amount": ["$1,200.50", "\u20b92,500", "abc", None]})
    report = {}
    out = clean_numeric(df, ["amount"], report)
    assert out["amount"].iloc[0] == 1200.5
    assert out["amount"].iloc[1] == 2500
    assert pd.isna(out["amount"].iloc[2])
    assert report["amount_unparseable"] == 1


def test_parse_dates_mixed_formats_and_garbage():
    df = pd.DataFrame({"d": ["2026-01-05", "05/01/2026", "Jan 5, 2026", "not a date"]})
    report = {}
    out = parse_dates(df, ["d"], dayfirst=True, report=report)
    expected = pd.Timestamp("2026-01-05")
    assert out["d"].iloc[0] == expected
    assert out["d"].iloc[1] == expected
    assert out["d"].iloc[2] == expected
    assert pd.isna(out["d"].iloc[3])
    assert report["d_unparseable"] == 1


def test_parse_dates_dayfirst_false():
    df = pd.DataFrame({"d": ["05/01/2026"]})
    out = parse_dates(df, ["d"], dayfirst=False)
    assert out["d"].iloc[0] == pd.Timestamp("2026-05-01")


def test_map_values_standardizes_cities():
    df = pd.DataFrame({"city": ["bangalore", "BLR", "mysore"]})
    out = map_values(df, {"city": {"bangalore": "Bengaluru", "blr": "Bengaluru"}})
    assert list(out["city"]) == ["Bengaluru", "Bengaluru", "Mysore"]


def test_dedupe_exact_and_by_key():
    df = pd.DataFrame({"id": ["1", "1", "2", "2"], "name": ["A", "A", "B", "B2"]})
    r1 = {}
    assert len(dedupe(df, report=r1)) == 3
    assert r1["duplicates_removed"] == 1
    r2 = {}
    assert len(dedupe(df, key=["id"], report=r2)) == 2
    assert r2["duplicates_removed"] == 2


def test_handle_missing_policies():
    df = pd.DataFrame({"amount": [1.0, None, 3.0]})
    assert len(handle_missing(df, {"amount": "drop"})) == 2
    assert handle_missing(df, {"amount": "fill_zero"})["amount"].iloc[1] == 0
    flagged = handle_missing(df, {"amount": "flag"})
    assert list(flagged["amount_missing"]) == [False, True, False]


def test_config_rejects_unknown_key(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("dayfrist: true\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_config(str(bad))