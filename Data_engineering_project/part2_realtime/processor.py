# Removes duplicate passengers and adds the extra columns.
import logging

import numpy as np
import pandas as pd

try:
    from . import config
except ImportError:
    import config

log = logging.getLogger("part2.processor")


def process(df):
    before = len(df)
    df = df.drop_duplicates(subset=config.DEDUP_ON).reset_index(drop=True)
    log.info("Removed %d duplicate row(s)", before - len(df))

    sibsp = pd.to_numeric(df["SibSp"], errors="coerce")
    parch = pd.to_numeric(df["Parch"], errors="coerce")
    fare = pd.to_numeric(df["Fare"], errors="coerce")
    age = pd.to_numeric(df["Age"], errors="coerce")

    df["family_size"] = (sibsp + parch + 1).astype("Int64")
    df["is_alone"] = df["family_size"] == 1
    # the title is between the comma and dot in the name, e.g. "Braund, Mr. Owen" -> Mr
    df["title"] = df["Name"].str.extract(r",\s*([^.]+)\.")[0].str.strip()
    df["fare_per_person"] = (fare / df["family_size"]).round(2)
    df["age_group"] = pd.cut(age, config.AGE_BINS, labels=config.AGE_LABELS).astype("object")

    log.info("Processed: %d rows, %d columns", len(df), len(df.columns))
    return df
