import openpyxl
import pytest
from src.fhir_sheets.core.read_input import (
    process_sheet_patient_data_revised,
    read_xlsx_and_process,
)


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

    assert "the sheet ends at row 2, above the 6 header rows" in caplog.text
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


HEADER_LABELS = [
    "Entity To Query",
    "JsonPath",
    "Data Type",
    "Value Set",
    "Recommended Profile",
    "Data Element",
]


def build_workbook(path, patient_data_column, resource_type="Patient"):
    """Write a minimal workbook shaped like Fhir_Cohort_Import_Template.xlsx.

    Column A carries the row labels and column C onwards carries the data, which
    is why the reader starts at min_col=3. patient_data_column is written down
    column C from row 1, so a short list produces a sheet whose used range stops
    above the sixth header row.
    """
    workbook = openpyxl.Workbook()

    definitions = workbook.active
    definitions.title = "ResourceDefinitions"
    definitions.append(["Entity Name", "ResourceType", "Profile(s)"])
    definitions.append(["description row", "description row", "description row"])
    definitions.append(["PrimaryPatient", resource_type, ""])

    links = workbook.create_sheet("ResourceLinks")
    links.append(["OriginResource", "ReferencePath", "DestinationResource"])
    links.append(["description row", "description row", "description row"])

    patient_data = workbook.create_sheet("PatientData")
    for row, label in enumerate(HEADER_LABELS, start=1):
        patient_data.cell(row=row, column=1, value=label)
    for row, value in enumerate(patient_data_column, start=1):
        patient_data.cell(row=row, column=3, value=value)

    workbook.save(path)
    return path


def test_read_xlsx_and_process_with_a_truncated_patient_data_sheet(tmp_path):
    """A PatientData tab whose used range stops above the Data Element row.

    This is the shape that raised "IndexError: tuple index out of range" out of
    read_xlsx_and_process, with nothing in the traceback naming the sheet or the
    column.
    """
    path = build_workbook(
        tmp_path / "truncated.xlsx",
        ["PrimaryPatient", "name[0].given[0]", "string"],
    )

    _definitions, _links, cohort_data = read_xlsx_and_process(path)

    assert len(cohort_data.headers) == 1
    header = cohort_data.headers[0]
    assert header.entityName == "PrimaryPatient"
    assert header.jsonPath == "name[0].given[0]"
    assert cohort_data.patients == []


def test_read_xlsx_and_process_with_a_complete_patient_data_sheet(tmp_path):
    """The same workbook filled in, so the fix cannot pass by dropping columns."""
    path = build_workbook(
        tmp_path / "complete.xlsx",
        [
            "PrimaryPatient",
            "name[0].given[0]",
            "string",
            "",
            "",
            "First Name",
            "Ada",
            "Grace",
        ],
    )

    _definitions, _links, cohort_data = read_xlsx_and_process(path)

    header = cohort_data.headers[0]
    assert header.entityName == "PrimaryPatient"
    assert header.fieldName == "First Name"
    assert cohort_data.get_num_patients() == 2
