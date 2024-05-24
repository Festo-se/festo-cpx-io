"""Channel builder functions from APDD"""

from dataclasses import dataclass
from typing import List


@dataclass
class ChannelGroup:
    """ChannelGroup dataclass"""

    channel_group_id: int
    channels: dict
    name: str
    parameter_group_ids: List[int]


@dataclass
class Channel:
    """Channel dataclass"""

    # pylint: disable=too-many-instance-attributes
    array_size: int
    bits: int
    byte_swap_needed: bool
    channel_id: int
    data_type: str
    description: str
    direction: str
    name: str
    parameter_group_ids: List[int]
    profile_list: list


def build_channel_group(channel_group_dict):
    """Builds one ChannelGroup"""
    return ChannelGroup(
        channel_group_dict.get("ChannelGroupId"),
        channel_group_dict.get("Channels"),
        channel_group_dict.get("Name"),
        channel_group_dict.get("ParameterGroupIds"),
    )


def build_channel(channel_dict):
    """Builds one Channel"""
    return Channel(
        channel_dict.get("ArraySize"),
        channel_dict.get("Bits"),
        channel_dict.get("ByteSwapNeeded"),
        channel_dict.get("ChannelId"),
        channel_dict.get("DataType"),
        channel_dict.get("Description"),
        channel_dict.get("Direction"),
        channel_dict.get("Name"),
        channel_dict.get("ParameterGroupIds"),
        channel_dict.get("ProfileList"),
    )


def build_channel_list(apdd, variant, direction=None):
    """Builds one ChannelList"""
    if not apdd.get("ChannelGroups"):
        return []

    channel_group_list = [
        build_channel_group(d)
        for d in apdd.get("ChannelGroups")
        if d.get("ChannelGroupId") in variant.channel_group_ids
    ]
    channel_group_dict = {
        c.get("ChannelId"): c
        for channel_group in channel_group_list
        for c in channel_group.channels
    }
    channel_type_list = [build_channel(d) for d in apdd.get("Channels")]

    # combine all channels for the module
    channel_list = []
    for channel_type in channel_type_list:
        if channel_type.channel_id in channel_group_dict:
            num_channels = channel_group_dict[channel_type.channel_id]["Count"]
            channel_list += [channel_type] * num_channels

    # split them in input and output channels
    if direction is not None:
        channel_list = [c for c in channel_list if c.direction == direction]
    return channel_list
