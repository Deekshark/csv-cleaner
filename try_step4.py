import pandas as pd
from cleaner.steps import (normalize_headers, clean_strings, clean_numeric,
                           parse_dates, map_values, dedupe)

report = {}
df = pd.read_csv("sample_data/messy.csv", dtype=str)
report["rows_in"] = len(df)

df = normalize_headers(df)
df = clean_strings(df)
df = clean_numeric(df, ["amount"], report)
df = parse_dates(df, ["signup_date"], dayfirst=True, report=report)
df = map_values(df, {"city": {"bangalore": "Bengaluru", "blr": "Bengaluru"}})
df = dedupe(df, key=["customer_id"], report=report)

report["rows_out"] = len(df)
print(df[["customer_id", "signup_date", "amount", "city"]].to_string())
print()
print(report)
print("cities:", sorted(df["city"].dropna().unique()))