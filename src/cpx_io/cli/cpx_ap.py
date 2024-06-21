"""CLI tool to execute cpx_ap tasks."""

from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp

# pylint: disable=duplicate-code
# intended: cpx-e and cpx-ap have similar parser options


def add_cpx_ap_parser(subparsers):
    """Adds arguments to a provided subparsers instance"""
    parser = subparsers.add_parser("cpx-ap")
    parser.set_defaults(func=cpx_ap_func)

    parser.add_argument(
        "-si",
        "--system-information",
        action="store_true",
        help="Print system information",
    )
    parser.add_argument(
        "-ss", "--system-state", action="store_true", help="Print system state"
    )

    subparsers_cpx_ap = parser.add_subparsers(
        dest="subcommand",
        title="action commands",
        description="Action to perform",
    )
    parser_read = subparsers_cpx_ap.add_parser("read")
    parser_read.add_argument(
        "-m",
        "--module-index",
        type=int,
        default=1,
        help="Module index to read (default: %(default)s).",
    )
    parser_read.add_argument(
        "-c",
        "--channel-index",
        type=int,
        default=0,
        help="Channel index to be read (default: %(default)s)",
    )

    parser_write = subparsers_cpx_ap.add_parser("write")
    parser_write.add_argument(
        "-m",
        "--module-index",
        type=int,
        default=1,
        help="Module index to write (default: %(default)s).",
    )
    parser_write.add_argument(
        "-c",
        "--channel-index",
        type=int,
        default=0,
        help="Channel index to be written (default: %(default)s)",
    )
    parser_write.add_argument(
        "value",
        nargs="+",
        type=int,
        default=1,
        help="Value to be written (default: %(default)s).",
    )


def cpx_ap_func(args):
    """Executes subcommand based on provided arguments"""
    cpx_ap = CpxAp(ip_address=args.ip_address, timeout=0.0)
    if not cpx_ap.connected():
        return

    if args.system_information:
        cpx_ap.print_system_information()
    if args.system_state:
        cpx_ap.print_system_state()

    if args.subcommand == "read":
        value = cpx_ap.modules[args.module_index][args.channel_index]
        print(f"Value: {value}")

    elif args.subcommand == "write":
        cpx_ap.modules[args.module_index][args.channel_index] = args.value[0] > 0

    cpx_ap.shutdown()
