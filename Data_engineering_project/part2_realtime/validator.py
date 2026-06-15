# Validates the data against the rules in config, plus a check after processing.
import logging

import numpy as np
import pandas as pd

try:
    from . import config
except ImportError:
    import config

log = logging.getLogger("part2.validator")


def _flag(reason, mask, text):
    # set the reason on rows that just failed, but keep the first reason found
    newly = mask & (reason == "")
    reason[newly] = text


def validate(df):
    # Returns (clean rows, rejected rows). Rejected rows get a "reject_reason" column.
    df = df.replace(r"^\s*$", np.nan, regex=True)
    reason = pd.Series("", index=df.index)

    for col, rule in config.RULES.items():
        if col not in df.columns:
            raise ValueError(f"Expected column missing from file: {col}")

        empty = df[col].isna()
        if rule.get("required"):
            _flag(reason, empty, f"{col}: required value missing")

        present = ~empty
        if rule["type"] == "number":
            values = pd.to_numeric(df[col], errors="coerce")
            _flag(reason, present & values.isna(), f"{col}: not a number")
            if "min" in rule:
                _flag(reason, present & (values < rule["min"]), f"{col}: below minimum")
            if "max" in rule:
                _flag(reason, present & (values > rule["max"]), f"{col}: above maximum")
        elif rule["type"] == "date":
            _flag(reason, present & pd.to_datetime(df[col], errors="coerce").isna(),
                  f"{col}: invalid date")
        else:  # text
            if "pattern" in rule:
                ok = df[col].astype(str).str.fullmatch(rule["pattern"])
                _flag(reason, present & ~ok.fillna(False), f"{col}: wrong format")
            if "allowed" in rule:
                _flag(reason, present & ~df[col].isin(rule["allowed"]),
                      f"{col}: not an allowed value")

    bad = reason != ""
    log.info("Validation: %d row(s) ok, %d rejected", int((~bad).sum()), int(bad.sum()))

    clean = df[~bad].copy()
    rejected = df[bad].copy()
    if len(rejected):
        rejected["reject_reason"] = reason[bad]
    return clean, rejected


def backup_check(df):
    for col in ["family_size", "is_alone", "title", "fare_per_person", "age_group"]:
        if col not in df.columns:
            raise ValueError(f"Processing did not create column: {col}")
    assert df[config.DEDUP_ON].is_unique, "duplicates still present after processing"
    log.info("Backup check passed")
    return df
