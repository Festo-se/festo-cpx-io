"""CPX-E-1CI module implementation"""

from cpx_io.utils.logging import Logging
from cpx_io.cpx_system.cpx_e.cpx_e_module import CpxEModule  # pylint: disable=E0611


class CpxE1Ci(CpxEModule):
    """Class for CPX-E-1CI counter module"""

    # TODO: Add 1Cl module
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        raise NotImplementedError("The module CPX-E-1CI has not yet been implemented")
