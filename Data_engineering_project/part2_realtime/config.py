# Settings for Part 2. Set up for the Titanic dataset (lots of missing
# Age/Cabin/Embarked values). For another dataset, change RULES, DEDUP_ON and
# the extra columns in processor.py.
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(HERE)
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)   # needed to import storage.py

INPUT_DIR = os.path.join(HERE, "input")
OUTPUT_DIR = os.path.join(HERE, "output")
ARCHIVE_DIR = os.path.join(HERE, "archive")
ERROR_DIR = os.path.join(ARCHIVE_DIR, "errors")

ALLOWED_EXTENSIONS = (".csv", ".xlsx", ".xls")
DEDUP_ON = "PassengerId"   # same PassengerId = duplicate

# Rules per column. A missing "required" value gets the row dropped.
# Age/Ticket/Fare/Cabin/Embarked are optional since the real data misses a lot
# of them, so we keep those rows instead of throwing them out.
RULES = {
    "PassengerId": {"type": "number", "required": True},
    "Survived":    {"type": "number", "required": True, "min": 0, "max": 1},
    "Pclass":      {"type": "number", "required": True, "min": 1, "max": 3},
    "Name":        {"type": "text",   "required": True},
    "Sex":         {"type": "text",   "required": True, "allowed": ["male", "female"]},
    "Age":         {"type": "number", "required": False, "min": 0, "max": 120},
    "SibSp":       {"type": "number", "required": True, "min": 0, "max": 20},
    "Parch":       {"type": "number", "required": True, "min": 0, "max": 20},
    "Ticket":      {"type": "text",   "required": False},
    "Fare":        {"type": "number", "required": False, "min": 0},
    "Cabin":       {"type": "text",   "required": False},
    "Embarked":    {"type": "text",   "required": False, "allowed": ["S", "C", "Q"]},
}

# age groups: Child 0-12, Teen 13-18, Adult 19-60, Senior 60+
AGE_BINS = [-1, 12, 18, 60, 200]
AGE_LABELS = ["Child", "Teen", "Adult", "Senior"]
