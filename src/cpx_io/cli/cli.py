"""CLI Tool that distributes subcommands"""
import argparse
import logging
from cpx_io.cli.cpx_e import add_cpx_e_parser
from cpx_io.utils.logging import Logging


def main():
    """Parses command line arguments and calls corresponding subcommand program."""
    # Bus agnostic options
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-i",
        "--ip-address",
        default="192.168.0.1",
        help="IP address to connect to (default: %(default)s).",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="increase output verbosity"
    )

    subparsers = parser.add_subparsers(
        dest="subcommand",
        required=True,
        title="subcommands",
        help="Subcommand that should be called",
    )

    # Options for position
    add_cpx_e_parser(subparsers)

    args = parser.parse_args()

    if args.verbose:
        Logging(logging.INFO)
    else:
        Logging(logging.WARNING)

    args.func(args)


if __name__ == "__main__":
    main()
