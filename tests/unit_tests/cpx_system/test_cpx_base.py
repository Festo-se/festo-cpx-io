"""Contains tests for CpxBase class"""

from unittest.mock import Mock, patch
from dataclasses import dataclass
import pytest

from pymodbus.client import ModbusTcpClient
from cpx_io.cpx_system.cpx_base import CpxBase, CpxInitError


class TestCpxBase:
    "Test CpxBase methods"

    def test_constructor_no_ip(self):
        "Test constructor"
        # Arrange

        # Act
        cpx = CpxBase()

        # Assert
        assert isinstance(cpx, CpxBase)

    @patch("cpx_io.cpx_system.cpx_base.ModbusTcpClient", spec=True)
    def test_constructor_with_ip(self, mock_modbus_client):
        "Test constructor"
        # Arrange

        # Act
        cpx = CpxBase("192.168.1.1")

        # Assert
        assert isinstance(cpx, CpxBase)
        assert isinstance(cpx.client, ModbusTcpClient)

    def test_context_manager_no_ip(self):
        "Test context manager"
        # Arrange

        # Act
        with CpxBase() as cpx:

            # Assert
            assert isinstance(cpx, CpxBase)

    @patch("cpx_io.cpx_system.cpx_base.ModbusTcpClient", spec=True)
    def test_context_manager_with_ip(self, mock_modbus_client):
        "Test context manager"
        # Arrange

        # Act
        with CpxBase("192.168.1.1") as cpx:

            # Assert
            assert isinstance(cpx, CpxBase)
            assert isinstance(cpx.client, ModbusTcpClient)

    def test_read_device_info(self):
        "Test read_device_info"
        # Arrange
        cpx = CpxBase()

        class mock_rres:
            "mock ReadDeviceInformationRequest data"

            information = [
                b"Festo SE & Co. KG",
                b"CPX-E-EP",
                b"1.2",
                b"http://www.festo.com",
                b"Modbus TCP",
                b"CPX-E-Terminal",
            ]

        cpx.client = Mock(execute=Mock(return_value=mock_rres()))

        # Act
        info = cpx.read_device_info()

        # Assert
        assert info["vendor_name"] == "Festo SE & Co. KG"
        assert info["product_code"] == "CPX-E-EP"
        assert info["revision"] == "1.2"
        assert info["vendor_url"] == "http://www.festo.com"
        assert info["product_name"] == "Modbus TCP"
        assert info["model_name"] == "CPX-E-Terminal"

    def test_bitwiseReg8_from_bytes(self):
        "Test bitwiseReg functions"

        # Arrange
        @dataclass
        class TestRegister(CpxBase.BitwiseReg8):
            """register dataclass"""

            bit0: bool
            bit1: bool
            bit2: bool
            bit3: bool
            bit4: bool
            bit5: bool
            bit6: bool
            bit7: bool

        # Act
        reg = TestRegister.from_bytes(b"\xaa")

        # Assert
        reg.bit0 = True
        reg.bit1 = False
        reg.bit2 = True
        reg.bit3 = False
        reg.bit4 = True
        reg.bit5 = False
        reg.bit6 = True
        reg.bit7 = False

    def test_bitwiseReg8_from_int(self):
        "Test bitwiseReg functions"

        # Arrange
        @dataclass
        class TestRegister(CpxBase.BitwiseReg8):
            """register dataclass"""

            bit0: bool
            bit1: bool
            bit2: bool
            bit3: bool
            bit4: bool
            bit5: bool
            bit6: bool
            bit7: bool

        # Act
        reg = TestRegister.from_int(0xAA)

        # Assert
        reg.bit0 = True
        reg.bit1 = False
        reg.bit2 = True
        reg.bit3 = False
        reg.bit4 = True
        reg.bit5 = False
        reg.bit6 = True
        reg.bit7 = False

    def test_bitwiseReg8_to_int(self):
        "Test bitwiseReg functions"

        # Arrange
        @dataclass
        class TestRegister(CpxBase.BitwiseReg8):
            """register dataclass"""

            bit0: bool = False
            bit1: bool = True
            bit2: bool = False
            bit3: bool = True
            bit4: bool = False
            bit5: bool = True
            bit6: bool = False
            bit7: bool = True

        # Act
        reg = TestRegister()
        integer = reg.to_bytes()

        # Assert
        assert integer == b"\xaa"

    def test_bitwiseReg16_from_bytes(self):
        "Test bitwiseReg functions"

        # Arrange
        @dataclass
        class TestRegister(CpxBase.BitwiseReg16):
            """register dataclass"""

            bit0: bool
            bit1: bool
            bit2: bool
            bit3: bool
            bit4: bool
            bit5: bool
            bit6: bool
            bit7: bool
            bit8: bool
            bit9: bool
            bit10: bool
            bit11: bool
            bit12: bool
            bit13: bool
            bit14: bool
            bit15: bool

        # Act
        reg = TestRegister.from_bytes(b"\xaa\xff")

        # Assert
        reg.bit0 = True
        reg.bit1 = False
        reg.bit2 = True
        reg.bit3 = False
        reg.bit4 = True
        reg.bit5 = False
        reg.bit6 = True
        reg.bit7 = False
        reg.bit8 = True
        reg.bit9 = True
        reg.bit10 = True
        reg.bit11 = True
        reg.bit12 = True
        reg.bit13 = True
        reg.bit14 = True
        reg.bit15 = True

    def test_bitwiseReg16_from_int(self):
        "Test bitwiseReg functions"

        # Arrange
        @dataclass
        class TestRegister(CpxBase.BitwiseReg16):
            """register dataclass"""

            bit0: bool
            bit1: bool
            bit2: bool
            bit3: bool
            bit4: bool
            bit5: bool
            bit6: bool
            bit7: bool
            bit8: bool
            bit9: bool
            bit10: bool
            bit11: bool
            bit12: bool
            bit13: bool
            bit14: bool
            bit15: bool

        # Act
        reg = TestRegister.from_int(0xAAFF)

        # Assert
        reg.bit0 = True
        reg.bit1 = False
        reg.bit2 = True
        reg.bit3 = False
        reg.bit4 = True
        reg.bit5 = False
        reg.bit6 = True
        reg.bit7 = False
        reg.bit8 = True
        reg.bit9 = True
        reg.bit10 = True
        reg.bit11 = True
        reg.bit12 = True
        reg.bit13 = True
        reg.bit14 = True
        reg.bit15 = True

    def test_bitwiseReg16_to_int(self):
        "Test bitwiseReg functions"

        # Arrange
        @dataclass
        class TestRegister(CpxBase.BitwiseReg16):
            """register dataclass"""

            bit0: bool = False
            bit1: bool = True
            bit2: bool = False
            bit3: bool = True
            bit4: bool = False
            bit5: bool = True
            bit6: bool = False
            bit7: bool = True
            bit8: bool = True
            bit9: bool = True
            bit10: bool = True
            bit11: bool = True
            bit12: bool = True
            bit13: bool = True
            bit14: bool = True
            bit15: bool = True

        # Act
        reg = TestRegister()
        integer = reg.to_bytes()

        # Assert
        assert integer == b"\xaa\xff"

    def test_bitwise_reg_int(self):
        "Test bitwiseReg functions"

        # Arrange
        @dataclass
        class TestRegister(CpxBase.BitwiseReg16):
            """register dataclass"""

            bit0: bool = False
            bit1: bool = True
            bit2: bool = False
            bit3: bool = True
            bit4: bool = False
            bit5: bool = True
            bit6: bool = False
            bit7: bool = True
            bit8: bool = True
            bit9: bool = True
            bit10: bool = True
            bit11: bool = True
            bit12: bool = True
            bit13: bool = True
            bit14: bool = True
            bit15: bool = True

        # Act
        reg = TestRegister()
        integer = int(reg)

        # Assert
        assert integer == 0xFFAA

    def test_read_reg_data_without_length(self):
        "Test read_reg_data function"

        # Arrange
        class response:
            """mock response object"""

            def __init__(self):
                self.registers = [0]

            def isError(self):
                "mock error function"
                return False

        cpx = CpxBase()
        cpx.client = Mock(read_holding_registers=Mock(return_value=response()))

        # Act
        data = cpx.read_reg_data(0)

        # Assert
        assert data == b"\x00\x00"

    def test_read_reg_data_with_length(self):
        "Test read_reg_data function"

        # Arrange
        class response:
            """mock response object"""

            def __init__(self):
                self.registers = [0, 1, 2, 3]

            def isError(self):
                "mock error function"
                return False

        cpx = CpxBase()
        cpx.client = Mock(read_holding_registers=Mock(return_value=response()))

        # Act
        data = cpx.read_reg_data(0, 4)

        # Assert
        assert data == b"\x00\x00\x01\x00\x02\x00\x03\x00"

    def test_read_reg_data_error(self):
        "Test read_reg_data function"

        # Arrange
        class response:
            """mock response object"""

            def __init__(self):
                self.registers = [0, 1, 2, 3]
                self.message = "test"

            def isError(self):
                "mock error function"
                return True

        cpx = CpxBase()
        cpx.client = Mock(read_holding_registers=Mock(return_value=response()))

        # Act & Assert
        with pytest.raises(ConnectionAbortedError):
            cpx.read_reg_data(0)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            (b"\xaa", [0xAA]),
            (b"\xaa\xbb", [0xBBAA]),
            (b"\xaa\xbb\xcc", [0xBBAA, 0xCC]),
            (b"\xaa\xbb\xcc\xdd", [0xBBAA, 0xDDCC]),
        ],
    )
    def test_write_reg_data_nBytes(self, input_value, expected_value):
        "Test write_reg_data function"

        # Arrange
        cpx = CpxBase()
        cpx.client = Mock(write_registers=Mock())

        # Act
        cpx.write_reg_data(input_value, 0)

        # Assert
        cpx.client.write_registers.assert_called_with(0, expected_value)

    def test_require_base_missing(self):
        "Test require_base function"

        class testClass(CpxBase):

            @CpxBase.require_base
            def testFunction(self):
                return True

        # Arrange
        cpx = testClass()

        # Act & Assert
        with pytest.raises(CpxInitError):
            cpx.testFunction()

    def test_require_base_ok(self):
        "Test require_base function"

        class testClass(CpxBase):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.base = CpxBase()

            @CpxBase.require_base
            def testFunction(self):
                return True

        # Arrange
        cpx = testClass()

        # Act & Assert
        assert cpx.testFunction()
