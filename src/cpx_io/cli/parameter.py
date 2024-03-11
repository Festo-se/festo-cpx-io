"""CLI tool to execute parameter tasks."""

from cpx_io.cpx_system.parameter_mapping import ParameterMap
from cpx_io.utils.logging import Logging


def add_parameter_parser(subparsers):
    """Adds arguments to a provided subparsers instance"""
    parser = subparsers.add_parser("parameter")
    parser.set_defaults(func=parameter_func)

    parser.add_argument(
        "-l", "--list", action="store_true", help="Print list of parameters"
    )
    parser.add_argument(
        "-m",
        "--meta",
        default=20078,
        help="Print parameter meta data of given id (default: %(default)s).",
    )


def parameter_func(args):
    """Executes subcommand based on provided arguments"""

    parameter_map = ParameterMap()
    if args.list:
        Logging.logger.info(f"Number of entries: {len(parameter_map)}")
        for parameter in parameter_map:
            id_str = str(parameter.parameter_id).ljust(10)
            name_str = str(parameter.name).ljust(40)
            type_str = str(parameter.data_type).ljust(10)
            size_str = str(parameter.size).ljust(10)
            Logging.logger.info(
                f"id: {id_str} name: '{name_str}' type: '{type_str}' size: {size_str}"
            )
    if args.meta:
        parameter = parameter_map[int(args.meta)]
        if parameter:
            id_str = str(parameter.parameter_id).ljust(10)
            name_str = str(parameter.name).ljust(40)
            type_str = str(parameter.data_type).ljust(10)
            size_str = str(parameter.size).ljust(10)
            Logging.logger.info(
                f"id: {id_str} name: '{name_str}' type: '{type_str}' size: {size_str}"
            )
