# Settings for Part 1: paths, column lists and the validation rules.
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(HERE)
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)   # needed to import storage.py

DATA_DIR = os.path.join(HERE, "data")
OUTPUT_DIR = os.path.join(HERE, "output")

# These columns may be empty. Everything else has to have a value.
NON_MANDATORY = ["Suite/Condo", "Owner Name", "Address", "City", "State",
                 "Tax District", "image", "Foundation Type", "Exterior Wall", "Grade"]

# Columns to drop during processing.
DROP_COLUMNS = ["image", "Sold As Vacant", "Multiple Parcels Involved in Sale"]

# The Kaggle file has some weird header spacing, fix those to clean names.
RENAME = {
    "Suite/ Condo   #": "Suite/Condo",
    "Suite/Condo #": "Suite/Condo",
    "PropertyAddress": "Property Address",
    "OwnerAddress": "Address",
}

# Rules per column (type + range). Missing values are fine here, we deal with
# them in the processor.
RULES = {
    "Sale Date":      {"type": "date"},
    "Sale Price":     {"type": "number", "min": 0},
    "Acreage":        {"type": "number", "min": 0},
    "Land Value":     {"type": "number", "min": 0},
    "Building Value": {"type": "number", "min": 0},
    "Total Value":    {"type": "number", "min": 0},
    "Finished Area":  {"type": "number", "min": 0},
    "Year Built":     {"type": "number", "min": 1700, "max": 2026},
    "Bedrooms":       {"type": "number", "min": 0, "max": 50},
    "Full Bath":      {"type": "number", "min": 0, "max": 50},
    "Half Bath":      {"type": "number", "min": 0, "max": 50},
}

PRICE_LOW_MAX = 100_000
PRICE_HIGH_MIN = 300_000


def find_input():
    # use the env var if set, else the first real csv in data/, else the sample
    if os.getenv("PART1_INPUT_FILE"):
        return os.getenv("PART1_INPUT_FILE")
    for name in os.listdir(DATA_DIR):
        if name.lower().endswith(".csv") and "sample" not in name.lower():
            return os.path.join(DATA_DIR, name)
    return os.path.join(DATA_DIR, "sample_nashville.csv")
