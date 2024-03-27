"""AP product categories ENUMS"""

from enum import Enum


class ProductCategory(Enum):
    """Enum for ProductCategory"""

    INTERFACE = 10
    ANALOG = 20
    DIGITAL = 30
    MOTION = 40
    SERVO_DRIVES = 50
    SAFETY = 60
    IO_LINK = 61
    INFRASTRUCTURE = 70
    MPA_L = 80
    MPA_S = 81
    VTSA = 82
    VTUG = 83
    VTUX = 84
    VTOM = 85
    CONTROLLERS = 100
