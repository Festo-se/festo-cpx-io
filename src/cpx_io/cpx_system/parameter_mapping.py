"""Contains functions which provide mapping of Parameters."""

from collections import namedtuple
from importlib.resources import files
from pathlib import PurePath
from functools import lru_cache
import csv
from cpx_io.utils.logging import Logging


ParameterMapItem = namedtuple("ParameterMapItem", "parameter_id, name, data_type, size")


@lru_cache
def read_parameter_map_file(parameter_map_file: str = None) -> list:
    """Creates a list of parameter map items based on a provided parameter type map file

    Parameters:
        parameter_map_file (str): Optional file to use for mapping.
                                If nothing provided try to load mapping shipped with package.
    Returns:
        list: Containing parameter map items with fieldnames from the header parameter_map_file.
    """
    if not parameter_map_file:
        parameter_map_file = PurePath(
            files("cpx_io") / "cpx_system" / "data" / "parameter_map.csv"
        )
    with open(parameter_map_file, encoding="ascii") as csvfile:
        Logging.logger.info(f"Load parameter map file: {parameter_map_file}")
        reader = csv.reader(csvfile, delimiter=";")
        header = next(reader, None)
        Logging.logger.info(f"Header: {header}")
        # Use the following line to determine namedtuple fields directly from header
        # ParameterMapItem = namedtuple("ParameterMapItem", next(reader, None))

        # Interpret the first row element (parameter_id) as int
        return [ParameterMapItem(int(row[0]), *row[1:]) for row in reader]


@lru_cache
def create_parameter_map() -> dict:
    """Creates a dict based on a provided parameter map item list.
        It maps parameter ids to provided parameter map items

    Returns:
        dict: parameter ids (key) and parameter items (value)
    """
    parameter_list = read_parameter_map_file()
    Logging.logger.info("Create mapping from parameter ids to parameter items")
    return {item.parameter_id: item for item in parameter_list}


@lru_cache
def create_parameter_name_map() -> dict:
    """Creates a dict based on a provided parameter map item list.
        It maps parameter names to provided parameter map items

    Returns:
        dict: parameter name (key) and parameter items (value)
    """
    parameter_list = read_parameter_map_file()
    Logging.logger.info("Create mapping from parameter names to parameter items")
    return {item.name: item for item in parameter_list}


class ParameterMap:
    """Class that provides a mapping from parameter to parameter_map_item."""

    def __init__(self) -> None:
        self.mapping = create_parameter_map()

    def __iter__(self):
        return iter(self.mapping.values())

    def __getitem__(self, parameter: int):
        """Determines the corresponding parameter_map_item from a provided parameter number

        Parameters:
            parameter (int): parameter number.
        Returns:
            value: parameter_map_item
        """
        if parameter not in self.mapping:
            Logging.logger.error(
                f"Parameter {parameter} not available in parameter_map"
            )
            return None
        return self.mapping[parameter]

    def __len__(self):
        return len(self.mapping)


class ParameterNameMap:
    """Class that provides a mapping from parameter to parameter_map_item."""

    def __init__(self) -> None:
        self.mapping = create_parameter_name_map()

    def __iter__(self):
        return iter(self.mapping.values())

    def __getitem__(self, parameter_name: str):
        """Determines the corresponding parameter_map_item from a provided parameter name

        Parameters:
            parameter (str): parameter name.
        Returns:
            value: parameter_map_item
        """
        if parameter_name not in self.mapping:
            Logging.logger.error(
                f"Parameter {parameter_name} not available in parameter_map"
            )
            return None
        return self.mapping[parameter_name]

    def __len__(self):
        return len(self.mapping)
