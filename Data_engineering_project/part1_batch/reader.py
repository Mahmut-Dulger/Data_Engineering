# Reads the Nashville housing CSV and cleans up the column names.
import logging

import pandas as pd

try:
    from . import config
except ImportError:
    import config

log = logging.getLogger("part1.reader")


def read():
    path = config.find_input()
    log.info("Reading %s", path)
    df = pd.read_csv(path, dtype=str)
    df.columns = [c.strip() for c in df.columns]            # trim spaces in headers
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]   # drop the index columns
    df = df.rename(columns=config.RENAME)
    if df.empty:
        raise ValueError("Input file has no rows")
    log.info("Read %d rows, %d columns", len(df), len(df.columns))
    return df
