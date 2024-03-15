import json
from dataclasses import dataclass
from cpx_io.cpx_system.cpx_ap.cpx_ap_module import CpxApModule
from cpx_io.utils.boollist import bytes_to_boollist
from cpx_io.utils.helpers import div_ceil
from cpx_io.utils.logging import Logging

@dataclass
class Channel:
    bits : int
    channel_id : int
    data_type : str
    description : str
    direction : str
    name : str
    profile_list : list

@dataclass
class ChannelGroup:
    channel_group_id : int
    channels : dict
    name : str
    parameter_group_ids : list

class ChannelGroupBuilder:
    def build_channel_group(self, channel_group_dict):
        return ChannelGroup(channel_group_dict.get("ChannelGroupId"), 
                            channel_group_dict.get("Channels"),
                            channel_group_dict.get("Name"), 
                            channel_group_dict.get("ParameterGroupIds"),
                            )

class ChannelBuilder:
     def build_channel(self, channel_dict):
        return Channel(channel_dict.get("Bits"), 
                        channel_dict.get("ChannelId"),
                        channel_dict.get("DataType"), 
                        channel_dict.get("Description"),
                        channel_dict.get("Direction"), 
                        channel_dict.get("Name"), 
                        channel_dict.get("ProfileList"),
                        )
              

class GenericApModule(CpxApModule):

    def __init__(self, apdd_path=None):
        if apdd_path:
            with open(apdd_path, 'r', encoding='utf-8') as f:
                apdd = json.load(f)

            # set module code(s)
            module_codes = {}
            for variant in apdd["Variants"]["VariantList"]:
                module_codes[variant["VariantIdentification"]["ModuleCode"]] = variant["VariantIdentification"]["OrderText"]

            # setup all channel types
            channel_types = []
            for channel_dict in apdd["Channels"]:
                channel_types.append(ChannelBuilder().build_channel(channel_dict))

            Logging.logger.debug(f"Set up Channel Types: {channel_types}")

            # setup all channel groups
            channel_groups = []
            for channel_group_dict in apdd["ChannelGroups"]:
                channel_groups.append(ChannelGroupBuilder().build_channel_group(channel_group_dict))

            Logging.logger.debug(f"Set up Channel Groups: {channel_groups}")

            # setup all channels for the module
            channels = []
            for channel_group in channel_groups:
                for channel in channel_group.channels:
                    for channel_type in channel_types:
                        if channel_type.channel_id == channel.get("ChannelId"):
                            break
                    
                    for _ in range(channel["Count"]):
                        channels.append(channel_type)

            Logging.logger.debug(f"Set up Channels: {channels}")

            # split in in/out channels and set instance variables
            self.input_channels = [c for c in channels if c.direction=="in"]
            self.output_channels = [c for c in channels if c.direction=="out"]

    def read_channels(self):
        # if available, read inputs
        if self.input_channels:
            data = self.base.read_reg_data(self.input_register, 
                                           length=div_ceil(self.information.input_size, 2))
            if all(c.data_type == "BOOL" for c in self.input_channels):
                values = bytes_to_boollist(data)[:len(self.input_channels)]

        if self.output_channels:
            data = self.base.read_reg_data(self.output_register, 
                                           length=div_ceil(self.information.output_size, 2))
            if all(c.data_type == "BOOL" for c in self.output_channels):
                values = bytes_to_boollist(data)[:len(self.output_channels)]

        Logging.logger.info(f"{self.name}: Reading channels: {values}")
        return values


if __name__ == "__main__":
    Logging(logging_level="DEBUG")
    test = GenericApModule("APDD/CPX-AP-A-12DI4DO-M12-5P.json")