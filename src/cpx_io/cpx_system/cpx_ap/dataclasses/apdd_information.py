"""AP ApddInformation dataclass"""

from dataclasses import dataclass


@dataclass
class ApddInformation:
    """ApddInformation"""

    # pylint: disable=too-many-instance-attributes
    description: str
    name: str
    module_type: str
    configurator_code: str
    part_number: str
    module_class: str
    module_code: str
    order_text: str
    product_category: str
    product_family: str
