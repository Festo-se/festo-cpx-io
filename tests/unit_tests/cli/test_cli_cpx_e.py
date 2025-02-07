"""Contains tests for the cli of cpx-e """

import pytest
from unittest.mock import Mock, patch
from cpx_io.cli.cpx_e import add_cpx_e_parser, cpx_e_func
from cpx_io.cli.cli import main


def create_cli_params(param):
    param.setdefault("ip_address", "192.168.0.1")
    param.setdefault("typecode", "60E-EP-L")
    param.setdefault("subcommand", "cpx-e")
    param.setdefault("operation", "read")
    args_string = (
        [
            "cli.py",
            "-i",
            param["ip_address"],
            param["subcommand"],
            "-t",
            param["typecode"],
        ]
        + (["-m", param["module_index"]] if "module_index" in param else [])
        + [param["operation"]]
        + (["-c", param["channel_index"]] if "channel_index" in param else [])
    )
    if "value" in param:
        if isinstance(param["value"], list):
            args_string.extend(param["value"])
        else:
            args_string.append(param["value"])
    return args_string


# This fixture is here, so that the above function is not interpreted as test
@pytest.fixture(name="create_cli_params")
def create_cli_fixture():
    return create_cli_params({})


class TestCli:
    def test_add_cpx_e_parser(self):
        parser = Mock()
        parser_cpx_e = Mock()
        parser.add_parser = Mock(return_value=parser_cpx_e)
        add_cpx_e_parser(parser)
        parser.add_parser.assert_called_with("cpx-e")
        parser_cpx_e.set_defaults.assert_called_with(func=cpx_e_func)

    @patch("sys.argv", create_cli_params({"module_index": "2", "channel_index": "3"}))
    @patch("cpx_io.cli.cpx_e.CpxE")
    def test_cpe_x_func_read_with_channel_index(self, mocked_cpx_e, capfd):
        mocked_cpx_e.return_value.modules.__getitem__(2).__getitem__.return_value = True

        main()
        out, _ = capfd.readouterr()

        mocked_cpx_e.assert_called_with(
            ip_address="192.168.0.1",
            modules="60E-EP-L",
        )
        mocked_cpx_e.return_value.modules.__getitem__(2).__getitem__.assert_called_with(
            3
        )
        assert f"Value: True\n" in out

    @patch("sys.argv", create_cli_params({"module_index": "2"}))
    @patch("cpx_io.cli.cpx_e.CpxE")
    def test_cpe_x_func_read_without_channel_index(self, mocked_cpx_e, capfd):
        return_values = [False, True, False, False]
        mocked_cpx_e.return_value.modules.__getitem__(2).read_channels.return_value = (
            return_values
        )

        main()
        out, _ = capfd.readouterr()

        mocked_cpx_e.assert_called_with(
            ip_address="192.168.0.1",
            modules="60E-EP-L",
        )
        mocked_cpx_e.return_value.modules.__getitem__(2).read_channels.assert_called()
        assert f"Value: {return_values}" in out

    @patch(
        "sys.argv",
        create_cli_params(
            {
                "module_index": "2",
                "channel_index": "4",
                "operation": "write",
                "value": "True",
            }
        ),
    )
    @patch("cpx_io.cli.cpx_e.CpxE")
    def test_cpe_x_func_write_single_channel_index(self, mocked_cpx_e):

        main()

        mocked_cpx_e.assert_called_with(
            ip_address="192.168.0.1",
            modules="60E-EP-L",
        )
        mocked_cpx_e.return_value.modules.__getitem__(2).__setitem__.assert_called_with(
            4, True
        )

    @patch(
        "sys.argv",
        create_cli_params(
            {
                "module_index": "2",
                "channel_index": "4",
                "operation": "write",
            }
        ),
    )
    @patch("cpx_io.cli.cpx_e.CpxE")
    def test_cpe_x_func_write_single_channel_with_default(self, mocked_cpx_e):

        main()

        mocked_cpx_e.assert_called_with(
            ip_address="192.168.0.1",
            modules="60E-EP-L",
        )
        mocked_cpx_e.return_value.modules.__getitem__(2).__setitem__.assert_called_with(
            4, True
        )

    @patch(
        "sys.argv",
        create_cli_params(
            {
                "module_index": "2",
                "channel_index": "4",
                "operation": "write",
                "value": ["1", "0", "0", "1"],
            }
        ),
    )
    @patch("cpx_io.cli.cpx_e.CpxE")
    def test_cpe_x_func_write_single_channel_with_multiple_args(self, mocked_cpx_e):

        main()

        mocked_cpx_e.assert_called_with(
            ip_address="192.168.0.1",
            modules="60E-EP-L",
        )
        mocked_cpx_e.return_value.modules.__getitem__(2).__setitem__.assert_called_with(
            4, True
        )

    @patch(
        "sys.argv",
        create_cli_params(
            {
                "module_index": "2",
                "operation": "write",
                "value": ["1", "False", "false", "True"],
            }
        ),
    )
    @patch("cpx_io.cli.cpx_e.CpxE")
    def test_cpe_x_func_write_multiple_channels(self, mocked_cpx_e):

        main()

        mocked_cpx_e.assert_called_with(
            ip_address="192.168.0.1",
            modules="60E-EP-L",
        )

        mocked_cpx_e.return_value.modules.__getitem__(
            2
        ).write_channels.assert_called_with([True, False, False, True])
