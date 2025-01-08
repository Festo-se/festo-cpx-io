"""CLI Tool that distributes subcommands"""

import argparse
import logging
import pkg_resources
from cpx_io.cli.cpx_e import add_cpx_e_parser
from cpx_io.cli.cpx_ap import add_cpx_ap_parser
from cpx_io.utils.logging import Logging


def main():
    """Parses command line arguments and calls corresponding subcommand program."""

    # create arg parser just for version string without required arguments
    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument(
        "-v", "--version", action="store_true", help="print current version"
    )

    # parse known args breaks the help
    args, _ = parser.parse_known_args()

    if args.version:
        print(f"festo-cpx-io v{pkg_resources.require('festo-cpx-io')[0].version}")
        return

    # recreate argument parser for consistent help text
    # Bus agnostic options
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v", "--version", action="store_true", help="print current version"
    )
    parser.add_argument(
        "-i",
        "--ip-address",
        default="192.168.0.1",
        help="IP address to connect to (default: %(default)s).",
    )

    parser.add_argument(
        "-q", "--quiet", action="store_true", help="remove output verbosity"
    )

    subparsers = parser.add_subparsers(
        dest="subcommand",
        required=True,
        title="subcommands",
        help="Subcommand that should be called",
    )

    # Options for position
    add_cpx_e_parser(subparsers)
    add_cpx_ap_parser(subparsers)

    args = parser.parse_args()

    if args.quiet:
        Logging(logging.WARNING)
    else:
        Logging(logging.INFO)

    args.func(args)


if __name__ == "__main__":
    main()
