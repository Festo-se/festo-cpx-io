"""CPX-AP Enums for configure functions"""

from enum import Enum


class LoadSupplyEnum(Enum):
    """Enum for configure_monitoring_load_supply"""

    INACTIVE = 0
    ACTIVE_DIAG_OFF = 1
    ACTIVE = 2


class FailStateEnum(Enum):
    """Enum for configure_behaviour_in_fail_state"""

    RESET_OUTPUTS = 0
    HOLD_LAST_STATE = 1


class DebounceTimeEnum(Enum):
    """Enum for configure_debounce_time"""

    # pylint: disable=duplicate-code
    # intended: cpx-e and cpx-ap same debounce times

    T_100US = 0
    T_3MS = 1
    T_10MS = 2
    T_20MS = 3


class TempUnitEnum(Enum):
    """Enum for configure_channel_temp_unit"""

    CELSIUS = 0
    FARENHEIT = 1
    KELVIN = 2


class ChannelRangeEnum(Enum):
    """Enum for configure_channel_range
    * U means unipolar e.g. 0..10 V, 1..5 V
    * B means bipolar e.g. +/- 10 V"""

    NONE = 0
    B_10V = 1
    B_5V = 2
    U_10V = 3
    U_1_5V = 4
    U_20MA = 5
    U_4_20MA = 6
    U_500R = 7
    PT100 = 8
    NI100 = 9


class CycleTimeEnum(Enum):
    """Enum for configure_target_cycle_time"""

    FAST = 0
    T_1600US = 16
    T_3200US = 32
    T_4800US = 48
    T_8MS = 68
    T_10MS = 73
    T_12MS = 78
    T_16MS = 88
    T_20MS = 98
    T_40MS = 133
    T_80MS = 158
    T_120MS = 183


class PortModeEnum(Enum):
    """Enum for configure_port_mode"""

    DEACTIVATED = 0
    IOL_MANUAL = 1
    IOL_AUTOSTART = 2
    DI_CQ = 3
    PREOPERATE = 97


class ReviewBackupEnum(Enum):
    """Enum for configure_review_and_backup"""

    NO_TEST = 0
    COMPATIBLE_V1_0 = 1
    COMPATIBLE_V1_1 = 2
    COMPATIBLE_V1_1_DATA_BACKUP_RESTORE = 3
    COMPATIBLE_V1_1_DATE_RESTORE = 4
