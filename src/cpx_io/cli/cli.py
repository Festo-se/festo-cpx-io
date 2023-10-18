"""CLI Tool that distributes subcommands"""
import argparse


def main():
    """Parses command line arguments and calls corresponding subcommand program."""
    # Bus agnostic options
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--ip-address', default="192.168.0.1",
                        help='IP address to connect to (default: %(default)s).')

    subparsers = parser.add_subparsers(dest='subcommand', required=True,
                                       title='subcommands',
                                       help="Subcommand that should be called")

    args = parser.parse_args()

    args.func(args)


if __name__ == "__main__":
    main()
