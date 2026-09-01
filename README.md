# Qualtrics Wellbeing Validation
[![Tests](https://github.com/oyetzmedic/qualtrics-wellbeing-validation/actions/workflows/tests.yml/badge.svg)](https://github.com/oyetzmedic/qualtrics-wellbeing-validation/actions/workflows/tests.yml)



A small Python validation pipeline for checking exported Qualtrics wellbeing survey responses before downstream analysis.



The project demonstrates practical data-quality engineering around real survey-export structure, including Qualtrics metadata rows, response filtering, field validation, conditional logic, automated testing and generation of a validation report.



## What the pipeline does



`validate_qualtrics.py`:



- loads exactly one Qualtrics CSV from `data/raw/`

- skips the two Qualtrics metadata rows beneath the column-name header

- excludes Survey Preview records

- keeps only completed responses where `Finished == "True"` and `Progress == "100"`

- normalises the exported Q3 wellbeing field name

- validates allowed categorical responses

- validates sleep values between 0 and 24 hours

- validates exercise values between 0 and 7 days

- checks the conditional exercise-barrier question

- produces `data/processed/validation_report.csv`

- reports valid and invalid response counts



## Validation rules



The current validation includes:



- consent must be `Yes` or `No`

- age must match an allowed survey choice

- wellbeing response must match an allowed value

- five agreement-scale responses must contain allowed choices

- sleep must be between 0 and 24

- exercise must be between 0 and 7

- when exercise is 0, a valid barrier must be supplied

- when exercise is greater than 0, the barrier may be blank or an allowed choice



## Run locally



Place a Qualtrics CSV inside:



```text

data/raw/

```



Then run:



```bash

python validate_qualtrics.py

```



The script writes the validation report to:



```text

data/processed/validation_report.csv

```



## Tests



Run the automated tests with:



```bash

python -m pytest -q tests/test_validate_qualtrics.py

```



The tests currently verify that:



- a valid response passes with no validation errors

- a sleep value above 24 hours is rejected



## Data privacy



Raw Qualtrics exports and generated processed reports are intentionally excluded from version control through `.gitignore`.



This repository contains validation code and synthetic test data only. No survey-response CSV is committed.

