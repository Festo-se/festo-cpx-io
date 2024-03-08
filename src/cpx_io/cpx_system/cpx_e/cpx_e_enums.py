"""CPX-AP Enums for configure functions"""

from enum import Enum


class DebounceTime(Enum):
    """Enum for configure_debounce_time"""

    # pylint: disable=duplicate-code
    # intended: cpx-e and cpx-ap same debounce times

    T_100US = 0
    T_3MS = 1
    T_10MS = 2
    T_20MS = 3


class SignalExtension(Enum):
    """Enum for configure_signal_extension_time"""

    T_500US = 0
    T_15MS = 1
    T_50MS = 2
    T_100MS = 3


class ChannelRange(Enum):
    """Enum for configure_channel_range
    * U means unipolar e.g. 0..10 V, 1..5 V
    * B means bipolar e.g. +/- 10 V
    Not all modules accept all values"""

    NONE = 0
    U_10V = 1
    B_10V = 2
    B_5V = 3
    U_1_5V = 4
    U_20MA = 5
    U_4_20MA = 6
    B_20MA = 7
    U_10V_NO_UNDERDRIVE = 8
    U_20MA_NO_UNDERDRIVE = 9
    U_4_20MA_NO_UNDERDRIVE = 10


class DigInDebounceTime(Enum):
    """Enum for configure_debounce_time_for_digital_inputs"""

    T_20US = 0
    T_100US = 1
    T_3MS = 2


class IntegrationTime(Enum):
    """Enum for configure_integration_time_for_speed_measurement"""

    T_1MS = 0
    T_10MS = 1
    T_100MS = 2


class SignalType(Enum):
    """Enum for configure_signal_type"""

    ENCODER_5V_DIFFERENTIAL = 0
    ENCODER_5V_SINGLE_ENDED = 1
    ENCODER_24V_SINGLE_ENDED = 2


class SignalEvaluation(Enum):
    """Enum for configure_signal_evaluation"""

    INCREMENTAL_SINGLE_EVALUATION = 0
    INCREMENTAL_DOUBLE_EVALUATION = 1
    INCREMENTAL_QUADRUPLE_EVALUATION = 2
    PULSE_GENERATOR = 3


class LatchingEvent(Enum):
    """Enum for configure_latching_event"""

    RISING_EDGE = 1
    FALLING_EDGE = 2
    BOTH_EDGES = 3


class AddressSpace(Enum):
    """Enum for CpxE4Iol init"""

    PORT_2E2A = 2
    PORT_4E4A = 4
    PORT_8E8A = 8
    PORT_16E16A = 16
    PORT_32E32A = 32


class OperatingMode(Enum):
    """Enum for configure_operating_mode"""

    INACTIVE = 0
    DI = 1
    IO_LINK = 3
