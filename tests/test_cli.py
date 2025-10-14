import pathlib
import json
from typing import Iterable, Dict
from src.fhir_sheets.cli.main import main

TOP_DIR = pathlib.Path(__file__).parent.parent / "samples"

def test_congential_hyperthyrodism_excel_conversion(tmp_path):
    input_file = (TOP_DIR / "Congenital_Hyperthyrodism/Congenital_Hyperthyrodism_Fhir_Cohort_Import_Template.xlsx").__str__()
    main(input_file, tmp_path)

    json_files = list(tmp_path.glob("*.json"))
    json_file = json_files[0]
    with json_file.open('r') as file:
        fhir_bundle = json.load(file)

    assert fhir_bundle['resourceType'] == 'Bundle'
    assert fhir_bundle['type'] == 'transaction'