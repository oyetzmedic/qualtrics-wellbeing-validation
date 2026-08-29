import validate_qualtrics as v


def make_valid_row():
    return {
        "ResponseId": "TEST_001",
        "Status": "IP Address",
        "Finished": "True",
        "Progress": "100",
        "Q1_consent": "Yes",
        "Q2_age": "35–44",
        "Q3_wellbeing": "4",
        "Q4_1": "Agree",
        "Q4_2": "Agree",
        "Q4_3": "Agree",
        "Q4_4": "Agree",
        "Q4_5": "Agree",
        "Q5_sleep": "7",
        "Q6_exercise": "0",
        "Q7_barrier": "Lack of time",
    }

def test_valid_response_has_no_errors():
    row = make_valid_row()
    assert v.validate_response(row) == []

def test_sleep_above_24_is_rejected():
    row = make_valid_row()
    row["Q5_sleep"] = "25"

    assert "Q5_sleep must be between 0 and 24" in v.validate_response(row)