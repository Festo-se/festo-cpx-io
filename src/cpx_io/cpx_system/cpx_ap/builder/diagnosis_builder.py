"""ModuleDiagnosis builder functions from APDD"""

from cpx_io.cpx_system.cpx_ap.dataclasses.module_diagnosis import ModuleDiagnosis


def build_diagnosis(diagnosis_dict):
    """Builds one Diagnosis"""

    return ModuleDiagnosis(
        diagnosis_dict.get("Description"),
        diagnosis_dict.get("DiagnosisId"),
        diagnosis_dict.get("Guideline"),
        diagnosis_dict.get("Name"),
    )


def build_diagnosis_list(apdd) -> list:
    """Builds one DiagnosisList"""

    return [build_diagnosis(d) for d in apdd.get("Diagnoses").get("DiagnosisList")]
