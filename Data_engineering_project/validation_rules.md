# Validation rules

Both pipelines check every column before processing. A row that breaks a rule is
dropped and saved to output/rejected/ with the reason. The rules live in the
RULES dictionary in part1_batch/config.py and part2_realtime/config.py.

## Part 1 - Nashville housing

Optional columns (may be empty): Suite/Condo, Owner Name, Address, City, State,
Tax District, image, Foundation Type, Exterior Wall, Grade. Every other column is
mandatory.

Checks:
- Sale Date: must be a valid date
- Sale Price, Acreage, Land Value, Building Value, Total Value, Finished Area: number >= 0
- Year Built: number between 1700 and 2026
- Bedrooms, Full Bath, Half Bath: number between 0 and 50

Missing values are not rejected , rows that miss a
mandatory value are removed in the processing step instead.

## Part 2 - Titanic

| Column | Required | Rule |
|---|---|---|
| PassengerId | yes | number (also the duplicate key) |
| Survived | yes | 0 or 1 |
| Pclass | yes | between 1 and 3 |
| Name | yes | not empty |
| Sex | yes | male or female |
| Age | no | number between 0 and 120 |
| SibSp | yes | number between 0 and 20 |
| Parch | yes | number between 0 and 20 |
| Ticket | no | any text |
| Fare | no | number >= 0 |
| Cabin | no | any text |
| Embarked | no | S, C or Q |

Duplicate PassengerId rows are removed during processing.
