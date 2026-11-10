import yaml

DEFAULTS = {
    "date_columns": [],
    "dayfirst": True,
    "numeric_columns": [],
    "dedupe_key": None,
    "value_mappings": {},
    "missing": {},
}
VALID_MISSING = {"drop", "fill_zero", "flag"}


def load_config(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        user = yaml.safe_load(f) or {}

    unknown = set(user) - set(DEFAULTS)
    if unknown:
        raise ValueError(f"Unknown config keys: {sorted(unknown)}")

    cfg = {**DEFAULTS, **user}

    for col, policy in cfg["missing"].items():
        if policy not in VALID_MISSING:
            raise ValueError(
                f"Bad missing-value policy '{policy}' for '{col}'. "
                f"Choose from {sorted(VALID_MISSING)}."
            )
    return cfg