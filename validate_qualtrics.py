import csv
import glob
from pathlib import Path

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

QUESTION_FIELDS = [
    "Q1_consent",
    "Q2_age",
    "Q3_wellbeing",
    "Q4_1",
    "Q4_2",
    "Q4_3",
    "Q4_4",
    "Q4_5",
    "Q5_sleep",
    "Q6_exercise",
    "Q7_barrier",
]

AGE_CHOICES = {
    "18–24",
    "25–34",
    "35–44",
    "45–54",
    "55+",
    "Prefer not to say",
}

WELLBEING_CHOICES = {"1", "2", "3", "4", "5"}

AGREEMENT_CHOICES = {
    "Strongly disagree",
    "Disagree",
    "Neither agree nor disagree",
    "Agree",
    "Strongly agree",
}

BARRIER_CHOICES = {
    "Lack of time",
    "Lack of motivation",
    "Health or mobility issues",
    "Cost or access",
    "Other",
}

def load_qualtrics_rows():
    csv_files = list(RAW_DIR.glob("*.csv"))

    if len(csv_files) != 1:
        raise RuntimeError(
            f"Expected exactly 1 Qualtrics CSV in {RAW_DIR}, found {len(csv_files)}."
        )

    source_file = csv_files[0]

    with source_file.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)

        # Qualtrics exports two metadata rows after the column-name header:
        # question labels, then ImportId metadata.
        next(reader, None)
        next(reader, None)

        rows = list(reader)
        for row in rows:
            if "Q3_wellbieng" in row and "Q3_wellbeing" not in row:
                row["Q3_wellbeing"] = row.pop("Q3_wellbieng")

    return source_file, rows

def select_analysis_rows(rows):
    return [
        row
        for row in rows
        if row.get("Status", "").strip() != "Survey Preview"
        and row.get("Finished", "").strip() == "True"
        and row.get("Progress", "").strip() == "100"
    ]

def number_in_range(value, minimum, maximum):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return False

    return minimum <= number <= maximum

def validate_response(row):
    errors = []

    consent = row.get("Q1_consent", "").strip()

    if consent not in {"Yes", "No"}:
        errors.append("Q1_consent must be Yes or No")
        return errors

    if consent == "No":
        return errors

    if row.get("Q2_age", "").strip() not in AGE_CHOICES:
        errors.append("Invalid Q2_age")

    if row.get("Q3_wellbeing", "").strip() not in WELLBEING_CHOICES:
        errors.append("Invalid Q3_wellbeing")

    for field in ("Q4_1", "Q4_2", "Q4_3", "Q4_4", "Q4_5"):
        if row.get(field, "").strip() not in AGREEMENT_CHOICES:
            errors.append(f"Invalid {field}")

    if not number_in_range(row.get("Q5_sleep", "").strip(), 0, 24):
        errors.append("Q5_sleep must be between 0 and 24")

    exercise = row.get("Q6_exercise", "").strip()

    if not number_in_range(exercise, 0, 7):
        errors.append("Q6_exercise must be between 0 and 7")
    elif float(exercise) == 0:
        if row.get("Q7_barrier", "").strip() not in BARRIER_CHOICES:
            errors.append("Q7_barrier is required when Q6_exercise is 0")
    elif row.get("Q7_barrier", "").strip() not in {"", *BARRIER_CHOICES}:
        errors.append("Invalid Q7_barrier")

    return errors

def validate_rows(rows):
    results = []

    for row in rows:
        errors = validate_response(row)
        results.append(
            {
                "ResponseId": row.get("ResponseId", "").strip(),
                "valid": not errors,
                "errors": errors,
            }
        )

    return results
def write_validation_report(results):
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    output_file = PROCESSED_DIR / "validation_report.csv"

    with output_file.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["ResponseId", "valid", "errors"],
        )
        writer.writeheader()

        for result in results:
            writer.writerow(
                {
                    "ResponseId": result["ResponseId"],
                    "valid": result["valid"],
                    "errors": " | ".join(result["errors"]),
                }
            )

    return output_file


def main():
    source_file, rows = load_qualtrics_rows()
    selected_rows = select_analysis_rows(rows)
    results = validate_rows(selected_rows)
    report_file = write_validation_report(results)

    valid_count = sum(result["valid"] for result in results)

    print(f"Source: {source_file}")
    print(f"Completed non-preview responses: {len(selected_rows)}")
    print(f"Valid responses: {valid_count}")
    print(f"Invalid responses: {len(results) - valid_count}")
    print(f"Report: {report_file}")


if __name__ == "__main__":
    main()