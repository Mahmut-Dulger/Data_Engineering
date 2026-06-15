# Validates the data against the rules in config, plus a final check after processing.
import logging

import pandas as pd

try:
    from . import config
except ImportError:
    import config

log = logging.getLogger("part1.validator")


def validate(df):
    # Drop rows where a value is clearly wrong (bad type or out of range).
    # Missing values stay for now, the processor handles them.
    if df.empty:
        raise ValueError("Input file has no rows")

    bad = pd.Series(False, index=df.index)
    for col, rule in config.RULES.items():
        if col not in df.columns:
            raise ValueError(f"Expected column missing from file: {col}")

        if rule["type"] == "number":
            values = pd.to_numeric(df[col], errors="coerce")
        else:  # date
            values = pd.to_datetime(df[col], errors="coerce")

        present = df[col].notna() & (df[col].astype(str).str.strip() != "")
        bad |= present & values.isna()                  # value there but couldn't be parsed
        if "min" in rule:
            bad |= present & (values < rule["min"])
        if "max" in rule:
            bad |= present & (values > rule["max"])

    log.info("Validation: dropping %d row(s) with invalid values", int(bad.sum()))
    return df[~bad].copy()


def backup_check(df):
    # make sure processing actually produced the new columns before we save
    expected = ["Price Per Square Foot", "Sale Year", "Sale Month",
                "Age Of Property", "Land To Building Ratio", "Sale Price Category"]
    missing = [c for c in expected if c not in df.columns]
    if missing:
        raise ValueError(f"Processing did not create columns: {missing}")
    assert df["Sale Price Category"].dropna().isin(["Low", "Medium", "High"]).all()
    log.info("Backup check passed")
    return df
