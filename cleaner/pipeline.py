import json
import logging

import pandas as pd

from .config import load_config
from .steps import (normalize_headers, clean_strings, clean_numeric,
                    parse_dates, map_values, dedupe, handle_missing)

log = logging.getLogger(__name__)


def run(input_path: str, output_path: str, config_path: str,
        report_path: str = "report.json") -> dict:
    cfg = load_config(config_path)
    report = {}

    df = pd.read_csv(input_path, dtype=str, encoding="utf-8-sig")
    report["rows_in"] = len(df)
    log.info("Read %d rows from %s", len(df), input_path)

    # The order of the steps is visible right here, in one list.
    steps = [
        ("normalize headers", lambda d: normalize_headers(d)),
        ("clean strings",     lambda d: clean_strings(d)),
        ("clean numerics",    lambda d: clean_numeric(d, cfg["numeric_columns"], report)),
        ("parse dates",       lambda d: parse_dates(d, cfg["date_columns"], cfg["dayfirst"], report)),
        ("map values",        lambda d: map_values(d, cfg["value_mappings"])),
        ("dedupe",            lambda d: dedupe(d, cfg["dedupe_key"], report)),
        ("handle missing",    lambda d: handle_missing(d, cfg["missing"], report)),
    ]

    for name, step in steps:
        df = step(df)
        log.info("%s: %d rows", name, len(df))

    report["rows_out"] = len(df)

    df.to_csv(output_path, index=False, encoding="utf-8")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    log.info("Wrote %d rows to %s and report to %s",
             len(df), output_path, report_path)
    return report