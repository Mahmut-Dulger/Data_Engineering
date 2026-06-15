# Cleans the rows/columns and builds the extra columns we need.
import logging

import numpy as np
import pandas as pd

try:
    from . import config
except ImportError:
    import config

log = logging.getLogger("part1.processor")


def split_owner(name):
    # take the first owner and split into family + first name
    if not isinstance(name, str) or not name.strip():
        return (np.nan, np.nan)
    first_owner = name.split("&")[0].strip()
    if "," in first_owner:
        family, _, rest = first_owner.partition(",")
        first = rest.strip().split(" ")[0] if rest.strip() else np.nan
        return (family.strip(), first)
    parts = first_owner.split()
    return (parts[0], parts[1] if len(parts) > 1 else np.nan)


def price_category(price):
    if pd.isna(price):
        return np.nan
    if price < config.PRICE_LOW_MAX:
        return "Low"
    if price <= config.PRICE_HIGH_MIN:
        return "Medium"
    return "High"


def process(df):
    mandatory = [c for c in df.columns if c not in config.NON_MANDATORY]

    # drop rows that miss a mandatory value (count blank strings as missing)
    before = len(df)
    df = df.replace(r"^\s*$", np.nan, regex=True)
    df = df.dropna(subset=mandatory)
    log.info("Dropped %d rows missing mandatory values", before - len(df))

    df = df.drop(columns=[c for c in config.DROP_COLUMNS if c in df.columns])

    # convert the numbers we need
    price = pd.to_numeric(df["Sale Price"], errors="coerce")
    area = pd.to_numeric(df["Finished Area"], errors="coerce")
    year_built = pd.to_numeric(df["Year Built"], errors="coerce")
    land = pd.to_numeric(df["Land Value"], errors="coerce")
    building = pd.to_numeric(df["Building Value"], errors="coerce")
    sale_date = pd.to_datetime(df["Sale Date"], errors="coerce")

    # the new columns (replace(0, nan) avoids dividing by zero)
    df["Price Per Square Foot"] = (price / area.replace(0, np.nan)).round(2)
    df["Sale Year"] = sale_date.dt.year
    df["Sale Month"] = sale_date.dt.month
    df["Age Of Property"] = (df["Sale Year"] - year_built).clip(lower=0)
    df["Land To Building Ratio"] = (land / building.replace(0, np.nan)).round(4)
    df["Sale Price Category"] = price.apply(price_category)
    owners = df["Owner Name"].apply(split_owner)
    df["Owner Family Name"] = [o[0] for o in owners]
    df["Owner First Name"] = [o[1] for o in owners]

    log.info("Processed: %d rows, %d columns", len(df), len(df.columns))
    return df
