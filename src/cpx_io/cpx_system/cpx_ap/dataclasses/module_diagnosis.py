"""ModuleDiagnosis dataclass"""

from dataclasses import dataclass


@dataclass
class ModuleDiagnosis:
    """Diagnosis information of the module"""

    description: str
    diagnosis_id: str
    guideline: str
    name: str
