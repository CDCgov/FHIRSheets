import openpyxl
import pytest
from src.fhir_sheets.core.read_input import process_sheet_patient_data_revised


def make_patient_data_sheet(column_values):
    """Build a PatientData sheet with one populated column (column C)."""
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "PatientData"
    for row, value in enumerate(column_values, start=1):
        sheet.cell(row=row, column=3, value=value)
    return sheet


def test_patient_data_column_shorter_than_the_header_block():
    """A sheet that stops before row 6 has no Data Element cell to read.

    The six header rows are read by position, so col[5] raised
    "IndexError: tuple index out of range" and the run ended with no
    indication of which column or which rows were at fault.
    """
    sheet = make_patient_data_sheet(["Patient", "name[0].given[0]", "string"])

    cohort_data = process_sheet_patient_data_revised(sheet, [])

    assert len(cohort_data.headers) == 1
    header = cohort_data.headers[0]
    assert header.entityName == "Patient"
    assert header.jsonPath == "name[0].given[0]"
    assert header.valueType == "string"
    assert cohort_data.patients == []


def test_patient_data_short_column_warning(caplog):
    sheet = make_patient_data_sheet(["Patient", "name[0].given[0]"])

    with caplog.at_level("WARNING"):
        process_sheet_patient_data_revised(sheet, [])

    assert "only 2 of the 6 header rows" in caplog.text
    assert "column C" in caplog.text


def test_patient_data_full_column_is_unchanged():
    sheet = make_patient_data_sheet(
        [
            "Patient",
            "name[0].given[0]",
            "string",
            "http://example.org/vs",
            None,
            "First Name",
            "Ada",
            "Grace",
        ]
    )

    cohort_data = process_sheet_patient_data_revised(sheet, [])

    header = cohort_data.headers[0]
    assert header.fieldName == "First Name"
    assert header.valueSets == "http://example.org/vs"
    assert len(cohort_data.patients) == 2
