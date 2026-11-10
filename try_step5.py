import pandas as pd
from cleaner.config import load_config
from cleaner.steps import (normalize_headers, clean_strings, clean_numeric,
                           parse_dates, map_values, dedupe, handle_missing)

cfg = load_config("config.yaml")
report = {}

df = pd.read_csv("sample_data/messy.csv", dtype=str)
report["rows_in"] = len(df)

df = normalize_headers(df)
df = clean_strings(df)
df = clean_numeric(df, cfg["numeric_columns"], report)
df = parse_dates(df, cfg["date_columns"], cfg["dayfirst"], report)
df = map_values(df, cfg["value_mappings"])
df = dedupe(df, cfg["dedupe_key"], report)
df = handle_missing(df, cfg["missing"], report)

report["rows_out"] = len(df)
print(df[["customer_id", "amount", "amount_missing"]].to_string())
print()
print(report)