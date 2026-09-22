from pathlib import Path
import zipfile

from openpyxl import load_workbook

from src.fhir_sheets.core.read_input import (
    process_sheet_patient_data_revised,
    process_sheet_resource_definitions,
)


def test_patient_rows_are_independent_in_obesity_cohort(tmp_path):
    """Each Excel data row must remain independent after input processing."""
    archive_path = Path(__file__).parent.parent / "HCS_Cohort_set_v02.zip"
    workbook_path = tmp_path / "obesity_cohort.xlsx"

    with zipfile.ZipFile(archive_path) as archive:
        workbook_path.write_bytes(
            archive.read(
                "HCS_Cohort_set_v02/obesity_package_v01/obesity_cohort.xlsx"
            )
        )

    workbook = load_workbook(workbook_path, data_only=True)
    try:
        definitions = process_sheet_resource_definitions(
            workbook["ResourceDefinitions"]
        )
        cohort = process_sheet_patient_data_revised(
            workbook["PatientData"], definitions
        )
    finally:
        workbook.close()

    assert cohort.get_num_patients() == 50
    assert len({id(patient.entries) for patient in cohort.patients}) == 50

    first_patient = cohort.patients[0].entries
    last_patient = cohort.patients[-1].entries
    differing_fields = [
        field
        for field in first_patient.keys() & last_patient.keys()
        if first_patient[field] != last_patient[field]
    ]
    assert differing_fields
