# Validates the data against the rules in config, plus a check after processing.
import logging

import numpy as np
import pandas as pd

try:
    from . import config
except ImportError:
    import config

log = logging.getLogger("part2.validator")


def validate(df):
    df = df.replace(r"^\s*$", np.nan, regex=True)
    bad = pd.Series(False, index=df.index)

    for col, rule in config.RULES.items():
        if col not in df.columns:
            raise ValueError(f"Expected column missing from file: {col}")

        empty = df[col].isna()
        if rule.get("required"):
            bad |= empty                                   # required but empty

        present = ~empty
        if rule["type"] == "number":
            values = pd.to_numeric(df[col], errors="coerce")
            bad |= present & values.isna()                 # not a number
            if "min" in rule:
                bad |= present & (values < rule["min"])
            if "max" in rule:
                bad |= present & (values > rule["max"])
        elif rule["type"] == "date":
            bad |= present & pd.to_datetime(df[col], errors="coerce").isna()
        else:  # text
            if "pattern" in rule:
                ok = df[col].astype(str).str.fullmatch(rule["pattern"])
                bad |= present & ~ok.fillna(False)
            if "allowed" in rule:
                bad |= present & ~df[col].isin(rule["allowed"])

    log.info("Validation: dropping %d invalid row(s)", int(bad.sum()))
    return df[~bad].copy()


def backup_check(df):
    for col in ["family_size", "is_alone", "title", "fare_per_person", "age_group"]:
        if col not in df.columns:
            raise ValueError(f"Processing did not create column: {col}")
    assert df[config.DEDUP_ON].is_unique, "duplicates still present after processing"
    log.info("Backup check passed")
    return df
