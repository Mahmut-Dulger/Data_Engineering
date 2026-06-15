# Validates the data against the rules in config, plus a final check after processing.
import logging

import pandas as pd

try:
    from . import config
except ImportError:
    import config

log = logging.getLogger("part1.validator")


def _flag(reason, mask, text):
    # set the reason on rows that just failed, but keep the first reason found
    newly = mask & (reason == "")
    reason[newly] = text


def validate(df):
    # Returns (clean rows, rejected rows). A row is rejected if a value is clearly
    # wrong (bad type or out of range). Missing values are kept, the processor
    # deals with those. Rejected rows get a "reject_reason" column.
    if df.empty:
        raise ValueError("Input file has no rows")

    reason = pd.Series("", index=df.index)
    for col, rule in config.RULES.items():
        if col not in df.columns:
            raise ValueError(f"Expected column missing from file: {col}")

        if rule["type"] == "number":
            values = pd.to_numeric(df[col], errors="coerce")
        else:  # date
            values = pd.to_datetime(df[col], errors="coerce")

        present = df[col].notna() & (df[col].astype(str).str.strip() != "")
        _flag(reason, present & values.isna(), f"{col}: not a valid {rule['type']}")
        if "min" in rule:
            _flag(reason, present & (values < rule["min"]), f"{col}: below minimum")
        if "max" in rule:
            _flag(reason, present & (values > rule["max"]), f"{col}: above maximum")

    bad = reason != ""
    log.info("Validation: %d row(s) ok, %d rejected", int((~bad).sum()), int(bad.sum()))

    clean = df[~bad].copy()
    rejected = df[bad].copy()
    if len(rejected):
        rejected["reject_reason"] = reason[bad]
    return clean, rejected


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
