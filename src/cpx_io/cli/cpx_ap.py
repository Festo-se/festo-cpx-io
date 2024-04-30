"""CLI tool to execute cpx_ap tasks."""

from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp


def add_cpx_ap_parser(subparsers):
    """Adds arguments to a provided subparsers instance"""
    parser = subparsers.add_parser("cpx-ap")
    parser.set_defaults(func=cpx_ap_func)

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-si",
        "--system-information",
        action="store_true",
        help="Print system information",
    )
    group.add_argument(
        "-ss", "--system-state", action="store_true", help="Print system state"
    )


def cpx_ap_func(args):
    """Executes subcommand based on provided arguments"""
    cpx_ap = CpxAp(ip_address=args.ip_address)

    if args.system_information:
        cpx_ap.print_system_information()
    if args.system_state:
        cpx_ap.print_system_state()
