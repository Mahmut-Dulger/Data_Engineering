# Reads a dropped file (CSV or Excel) into a dataframe.
import os
import logging

import pandas as pd

try:
    from . import config
except ImportError:
    import config

log = logging.getLogger("part2.reader")


def read(path):
    ext = os.path.splitext(path)[1].lower()
    if ext not in config.ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}")
    log.info("Reading %s", path)
    df = pd.read_excel(path, dtype=str) if ext != ".csv" else pd.read_csv(path, dtype=str)
    df.columns = [c.strip() for c in df.columns]
    if df.empty:
        raise ValueError("File has no rows")
    log.info("Read %d rows, %d columns", len(df), len(df.columns))
    return df
