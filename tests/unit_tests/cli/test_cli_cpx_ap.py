"""Contains tests for cpx-ap cli"""

import pytest
from unittest.mock import Mock, patch
from cpx_io.cli.cpx_ap import add_cpx_ap_parser, cpx_ap_func
from cpx_io.cli.cli import main
from cpx_io.utils.helpers import ChannelIndexError


def create_cli_params(param):
    param.setdefault("ip_address", "192.168.0.1")
    param.setdefault("subcommand", "cpx-ap")
    param.setdefault("operation", "read")
    if "system_information" in param:
        return ["cli.py", "cpx-ap", "--system-information"]
    if "system_state" in param:
        return ["cli.py", "cpx-ap", "--system-state"]
    args_string = (
        [
            "cli.py",
            "-i",
            param["ip_address"],
            param["subcommand"],
            param["operation"],
        ]
        + (["-m", param["module_index"]] if "module_index" in param else [])
        + (["-c", param["channel_index"]] if "channel_index" in param else [])
        + ([param["value"]] if "value" in param else [])
    )
    return args_string


# This fixture is here, so that the above function is not interpreted as test
@pytest.fixture(name="create_cli_params")
def create_cli_fixture():
    return create_cli_params({})


class TestCli:

    def test_add_cpx_a_parser(self):
        parser = Mock()
        parser_cpx_ap = Mock()
        parser.add_parser = Mock(return_value=parser_cpx_ap)
        add_cpx_ap_parser(parser)
        parser.add_parser.assert_called_with("cpx-ap")
        parser_cpx_ap.set_defaults.assert_called_with(func=cpx_ap_func)

    @patch("sys.argv", create_cli_params({"module_index": "2", "channel_index": "3"}))
    @patch("cpx_io.cli.cpx_ap.CpxAp")
    def test_cpe_x_func_read_with_channel_index(self, mocked_cpx_ap, capfd):
        mocked_cpx_ap.return_value.modules.__getitem__(2).__getitem__.return_value = (
            True
        )

        main()
        out, _ = capfd.readouterr()

        mocked_cpx_ap.assert_called_with(
            ip_address="192.168.0.1",
            timeout=0.0,
        )
        mocked_cpx_ap.return_value.modules.__getitem__(
            2
        ).__getitem__.assert_called_with(3)
        assert f"Value: True\n" in out

    @patch("sys.argv", create_cli_params({"module_index": "2", "channel_index": "3"}))
    @patch("cpx_io.cli.cpx_ap.CpxAp")
    def test_cpe_x_func_read_with_channel_out_of_bounds(self, mocked_cpx_ap, capfd):
        mocked_cpx_ap.return_value.modules.__getitem__(2).__getitem__.side_effect = (
            ChannelIndexError()
        )
        main()
        _, stderr = capfd.readouterr()

        mocked_cpx_ap.assert_called_with(
            ip_address="192.168.0.1",
            timeout=0.0,
        )
        mocked_cpx_ap.return_value.modules.__getitem__(
            2
        ).__getitem__.assert_called_with(3)
        assert f"Error: channel index 3 does not exist\n" in stderr

    @patch("sys.argv", create_cli_params({"module_index": "2", "channel_index": "3"}))
    @patch("cpx_io.cli.cpx_ap.CpxAp")
    def test_cpe_x_func_read_with_module_out_of_bounds(self, mocked_cpx_ap, capfd):
        mocked_cpx_ap.return_value.modules.__getitem__.side_effect = IndexError()
        main()
        _, stderr = capfd.readouterr()

        mocked_cpx_ap.assert_called_with(
            ip_address="192.168.0.1",
            timeout=0.0,
        )
        mocked_cpx_ap.return_value.modules.__getitem__.assert_called_with(2)
        assert f"Error: module index 2 does not exist\n" in stderr

    @patch(
        "sys.argv",
        create_cli_params(
            {"module_index": "2", "channel_index": "3", "operation": "write"}
        ),
    )
    @patch("cpx_io.cli.cpx_ap.CpxAp")
    def test_cpe_x_func_write_with_channel_out_of_bounds(self, mocked_cpx_ap, capfd):
        mocked_cpx_ap.return_value.modules.__getitem__(2).__setitem__.side_effect = (
            ChannelIndexError()
        )
        main()
        _, stderr = capfd.readouterr()

        mocked_cpx_ap.assert_called_with(
            ip_address="192.168.0.1",
            timeout=0.0,
        )
        mocked_cpx_ap.return_value.modules.__getitem__(
            2
        ).__setitem__.assert_called_with(3, True)
        assert f"Error: channel index 3 does not exist\n" in stderr

    @patch(
        "sys.argv",
        create_cli_params(
            {"module_index": "2", "channel_index": "3", "operation": "write"}
        ),
    )
    @patch("cpx_io.cli.cpx_ap.CpxAp")
    def test_cpe_x_func_write_with_module_out_of_bounds(self, mocked_cpx_ap, capfd):
        mocked_cpx_ap.return_value.modules.__getitem__.side_effect = IndexError()
        main()
        _, stderr = capfd.readouterr()

        mocked_cpx_ap.assert_called_with(
            ip_address="192.168.0.1",
            timeout=0.0,
        )
        mocked_cpx_ap.return_value.modules.__getitem__.assert_called_with(2)
        assert f"Error: module index 2 does not exist\n" in stderr

    @patch(
        "sys.argv",
        create_cli_params(
            {
                "module_index": "2",
                "channel_index": "3",
                "operation": "write",
                "value": 0,
            }
        ),
    )
    @patch("cpx_io.cli.cpx_ap.CpxAp")
    def test_cpe_x_func_write_with_channel_index(self, mocked_cpx_ap):
        main()

        mocked_cpx_ap.assert_called_with(
            ip_address="192.168.0.1",
            timeout=0.0,
        )
        mocked_cpx_ap.return_value.modules.__getitem__(
            2
        ).__setitem__.assert_called_with(3, False)

    @patch(
        "sys.argv",
        create_cli_params(
            {
                "module_index": "5",
                "channel_index": "4",
                "operation": "write",
            }
        ),
    )
    @patch("cpx_io.cli.cpx_ap.CpxAp")
    def test_cpe_x_func_write_with_channel_index_and_default(self, mocked_cpx_ap):
        main()
        mocked_cpx_ap.assert_called_with(
            ip_address="192.168.0.1",
            timeout=0.0,
        )
        mocked_cpx_ap.return_value.modules.__getitem__(
            5
        ).__setitem__.assert_called_with(4, True)
