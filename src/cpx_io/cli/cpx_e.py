"""CLI tool to execute cpx_e tasks."""

import argparse
from cpx_io.cpx_system.cpx_e.cpx_e import CpxE

# pylint: disable=duplicate-code
# intended: cpx-e and cpx-ap have similar parser options


def str_to_bool(value):
    """Convert a string to a boolean value."""
    if value.lower() in ("true", "1"):
        return True
    if value.lower() in ("false", "0"):
        return False
    raise argparse.ArgumentTypeError(f"Invalid boolean value: {value}")


def add_cpx_e_parser(subparsers):
    """Adds arguments to a provided subparsers instance"""
    parser_cpx_e = subparsers.add_parser("cpx-e")
    parser_cpx_e.set_defaults(func=cpx_e_func)

    parser_cpx_e.add_argument(
        "-t", "--typecode", type=str, required=True, help="Typecode of the cpx setup"
    )
    parser_cpx_e.add_argument(
        "-m",
        "--module-index",
        type=int,
        default=1,
        help="Module index to read (default: %(default)s).",
    )

    subparsers_cpx = parser_cpx_e.add_subparsers(
        dest="subcommand",
        required=True,
        title="action commands",
        description="Action to perform",
    )

    parser_read = subparsers_cpx.add_parser(
        "read", help="if no channel is given, all channels are read"
    )
    parser_read.add_argument(
        "-c", "--channel-index", type=int, help="Channel index to be read"
    )

    parser_write = subparsers_cpx.add_parser(
        "write",
        help="if no channel is given, all channels are written if enough values are supplied",
    )
    parser_write.add_argument(
        "-c", "--channel-index", type=int, help="Channel index to be written"
    )
    parser_write.add_argument(
        "value",
        nargs="*",
        type=str_to_bool,
        default=[True],
        help="Value to be written (default: True).",
    )


def cpx_e_func(args):
    """Executes subcommand based on provided arguments"""
    cpx_e = CpxE(ip_address=args.ip_address, modules=args.typecode)

    if args.subcommand == "read":
        if args.channel_index is not None:
            value = cpx_e.modules[args.module_index][args.channel_index]
            print(f"Value: {value}")
        else:
            value = cpx_e.modules[args.module_index].read_channels()
            print(f"Value: {value}")

    elif args.subcommand == "write":
        if args.channel_index is not None:
            cpx_e.modules[args.module_index][args.channel_index] = args.value[0]
        else:
            value = cpx_e.modules[args.module_index].write_channels(args.value)
