"""Contains tests for ApModule class"""

from unittest.mock import Mock
import pytest

from cpx_io.cpx_system.cpx_ap.builder.channel_builder import (
    ChannelGroupBuilder,
    ChannelGroup,
    ChannelBuilder,
    Channel,
    ChannelListBuilder,
)


class TestChannelGroupBuilder:
    "Test ChannelGroupBuilder"

    def test_build(self):
        """Test configure"""
        # Arrange
        channel_group_id = 123
        channels = {"foo": "bar"}
        name = "TestChannelGroup"
        parameter_group_ids = [1, 2, 3, 4, 5]
        channel_group_dict = {
            "ChannelGroupId": channel_group_id,
            "Channels": channels,
            "Name": name,
            "ParameterGroupIds": parameter_group_ids,
        }

        # Act
        channel_group = ChannelGroupBuilder().build(channel_group_dict)

        # Assert
        assert isinstance(channel_group, ChannelGroup)
        assert channel_group.channel_group_id == channel_group_id
        assert channel_group.channels == channels
        assert channel_group.name == name
        assert channel_group.parameter_group_ids == parameter_group_ids


class TestChannelBuilder:
    "Test ChannelBuilder"

    def test_build(self):
        """Test configure"""
        # Arrange
        array_size = 5
        bits = 9
        byte_swap_needed = False
        channel_id = 7
        data_type = "int"
        description = "ChannelDescription"
        direction = "out"
        name = "foo"
        parameter_group_ids = [1, 2, 3, 4, 5]
        profile_list = ["a", "b", "c"]
        channel_dict = {
            "ArraySize": array_size,
            "Bits": bits,
            "ByteSwapNeeded": byte_swap_needed,
            "ChannelId": channel_id,
            "DataType": data_type,
            "Description": description,
            "Direction": direction,
            "Name": name,
            "ParameterGroupIds": parameter_group_ids,
            "ProfileList": profile_list,
        }

        # Act
        channel = ChannelBuilder().build(channel_dict)

        # Assert
        assert isinstance(channel, Channel)
        assert channel.array_size == array_size
        assert channel.bits == bits
        assert channel.byte_swap_needed == byte_swap_needed
        assert channel.channel_id == channel_id
        assert channel.data_type == data_type
        assert channel.description == description
        assert channel.direction == direction
        assert channel.name == name
        assert channel.parameter_group_ids == parameter_group_ids
        assert channel.profile_list == profile_list


class TestChannelListBuilder:
    "Test ChannelListBuilder"

    def get_test_channel_group_list(self):
        channel_group_dict_list = []
        for i in range(5):
            channel_group_id = i * 5
            name = f"TestChannelGroup{channel_group_id}"
            channels = [{"ChannelId": i, "Count": 2}]
            channel_group_dict = {
                "ChannelGroupId": channel_group_id,
                "Name": name,
                "Channels": channels,
                "ParameterGroupIds": [],
            }
            channel_group_dict_list.append(channel_group_dict)
        return channel_group_dict_list

    def get_test_channel_list(self):
        channel_dict_list = []
        for i in range(5):
            array_size = 5
            bits = 9
            byte_swap_needed = False
            channel_id = i
            data_type = "bool"
            description = f"Channel{i}Description"
            direction = "out"
            name = f"Channel{i}"
            channel_dict = {
                "ArraySize": array_size,
                "Bits": bits,
                "ByteSwapNeeded": byte_swap_needed,
                "ChannelId": channel_id,
                "DataType": data_type,
                "Description": description,
                "Direction": direction,
                "Name": name,
                "ParameterGroupIds": [],
                "ProfileList": [],
            }
            channel_dict_list.append(channel_dict)
        return channel_dict_list

    def test_build(self):
        # Arrange
        test_channel_group_dict_list = self.get_test_channel_group_list()
        test_channel_dict_list = self.get_test_channel_list()
        apdd = {
            "ChannelGroups": test_channel_group_dict_list,
            "Channels": test_channel_dict_list,
        }

        # Act
        channel_list = ChannelListBuilder().build(apdd=apdd)

        # Assert
        for channel in channel_list:
            assert isinstance(channel, Channel)
        assert len(channel_list) == 10
