"""Contains class which contains logging methods."""

import logging
import sys


class Logging:
    """Class that contains common functions for logging."""

    logger = logging.getLogger("cpx-io")

    def __init__(self, logging_level=logging.INFO, filename=None):
        try:
            # pylint: disable=import-outside-toplevel
            from rich.logging import RichHandler

            logging.basicConfig(
                format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
            )

            Logging.logger.setLevel(logging_level)
            Logging.logger.propagate = False

            if filename:
                self.enable_file_logging(filename, logging_level)
            else:
                self.enable_stream_logging(logging_level)
        except ModuleNotFoundError as error:
            print(f"Error: Missing logging dependencies - {error}")
            print("Please install cli dependencies with: pip install festo-cpx-io[cli]")
            sys.exit(1)

    def enable_stream_logging(self, logging_level):
        """Enables logging to stream using the provided log level with rich log formatting."""
        # pylint: disable=import-outside-toplevel
        from rich.logging import RichHandler

        handler = RichHandler()
        handler.setLevel(logging_level)
        formatter = logging.Formatter(fmt="%(message)s", datefmt="[%X]")
        handler.setFormatter(formatter)
        Logging.logger.addHandler(handler)

    def enable_file_logging(self, filename, logging_level):
        """Enables logging to a file using the provided filename and log level."""
        handler = logging.FileHandler(filename)
        handler.setLevel(logging_level)
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="[%X]"
        )
        handler.setFormatter(formatter)
        Logging.logger.addHandler(handler)
