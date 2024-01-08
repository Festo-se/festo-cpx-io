"""Contains tests for MotionHandler class"""
from unittest.mock import Mock
from cpx_io.cli.cpx_e import add_cpx_e_parser


class TestCli:
    def test_add_cpx_e_parser(self):
        parser = Mock()
        add_cpx_e_parser(parser)
        parser.add_parser.assert_called_with("cpx-e")
