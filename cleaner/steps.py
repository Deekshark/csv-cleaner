import re
import pandas as pd


def normalize_headers(df: pd.DataFrame) -> pd.DataFrame:
    """'Amount ($)' -> 'amount', 'SIGNUP DATE ' -> 'signup_date'."""
    df = df.copy()
    df.columns = [
        re.sub(r"[^a-z0-9]+", "_", str(c).strip().lower()).strip("_")
        for c in df.columns
    ]
    return df


def clean_strings(df: pd.DataFrame) -> pd.DataFrame:
    """Trim, collapse repeated spaces, and turn blank strings into nulls."""
    df = df.copy()
    for col in df.columns:
        if pd.api.types.is_string_dtype(df[col]) or df[col].dtype == object:
            df[col] = (
                df[col]
                .str.strip()
                .str.replace(r"\s+", " ", regex=True)
                .replace("", pd.NA)
            )
    return df


def dedupe(df: pd.DataFrame, key=None, report: dict | None = None) -> pd.DataFrame:
    """Drop exact duplicate rows (or duplicates on `key` columns)."""
    before = len(df)
    df = df.drop_duplicates(subset=key, keep="first")
    if report is not None:
        report["duplicates_removed"] = before - len(df)
    return df


def clean_numeric(df: pd.DataFrame, cols, report: dict | None = None) -> pd.DataFrame:
    """'$1,200.50' -> 1200.5. Anything that still isn't a number becomes null."""
    df = df.copy()
    for c in cols:
        if c not in df.columns:
            continue
        had_value = df[c].notna()
        # strip currency symbols (incl. rupee, euro, pound), commas, spaces
        stripped = df[c].str.replace(r"[$\u20b9\u20ac\u00a3,\s]", "", regex=True)
        df[c] = pd.to_numeric(stripped, errors="coerce")
        if report is not None:
            report[f"{c}_unparseable"] = int((had_value & df[c].isna()).sum())
    return df


def parse_dates(df: pd.DataFrame, cols, dayfirst: bool = True,
                report: dict | None = None) -> pd.DataFrame:
    """Try a list of explicit formats in order; unmatched values become null."""
    formats = [
        "%Y-%m-%d",
        "%d/%m/%Y" if dayfirst else "%m/%d/%Y",
        "%b %d, %Y",
        "%B %d, %Y",
    ]
    df = df.copy()
    for c in cols:
        if c not in df.columns:
            continue
        had_value = df[c].notna()
        parsed = pd.Series(pd.NaT, index=df.index, dtype="datetime64[ns]")
        for fmt in formats:
            parsed = parsed.fillna(pd.to_datetime(df[c], format=fmt, errors="coerce"))
        df[c] = parsed
        if report is not None:
            report[f"{c}_unparseable"] = int((had_value & df[c].isna()).sum())
    return df


def map_values(df: pd.DataFrame, mappings: dict) -> pd.DataFrame:
    """Apply per-column lookups (case-insensitive); unmapped values get Title Case."""
    df = df.copy()
    for col, mapping in mappings.items():
        if col not in df.columns:
            continue
        mapped = df[col].str.lower().map(mapping)
        df[col] = mapped.fillna(df[col].str.title())
    return df