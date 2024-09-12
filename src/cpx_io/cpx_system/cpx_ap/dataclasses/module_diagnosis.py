"""AP ModuleDiagnosis dataclass"""

from dataclasses import dataclass


@dataclass
class ModuleDiagnosis:
    """ModuleDiagnosis dataclass"""

    description: str
    diagnosis_id: str
    guideline: str
    name: str
