"""Contains tests for ApModule class"""

from unittest.mock import Mock
import pytest

from cpx_io.cpx_system.cpx_ap.builder.channel_builder import (
    ChannelGroup,
    Channel,
    build_channel_group,
    build_channel,
    build_channel_list,
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
        channel_group = build_channel_group(channel_group_dict)

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
        channel = build_channel(channel_dict)

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

    def get_test_channel_group_list(self, n_channel_groups, n_channels_per_group):
        channel_group_dict_list = []
        for i in range(n_channel_groups):
            channel_group_id = i
            name = f"TestChannelGroup{channel_group_id}"
            channels = [{"ChannelId": i, "Count": n_channels_per_group}]
            channel_group_dict = {
                "ChannelGroupId": channel_group_id,
                "Name": name,
                "Channels": channels,
                "ParameterGroupIds": [],
            }
            channel_group_dict_list.append(channel_group_dict)
        return channel_group_dict_list

    def get_test_channel_list(self, n_channels):
        channel_dict_list = []
        for i in range(n_channels):
            array_size = 0
            bits = 0
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

    def test_build_5channelsand2groupsof5_returnslistoflen10(self):
        # Arrange
        # channel_group ids = [[0,0,0,0,0],[1,1,1,1,1]]
        test_channel_group_dict_list = self.get_test_channel_group_list(2, 5)
        # channel ids = [0,1,2,3,4]
        test_channel_dict_list = self.get_test_channel_list(5)
        apdd = {
            "ChannelGroups": test_channel_group_dict_list,
            "Channels": test_channel_dict_list,
        }
        # Act
        channel_list = build_channel_list(apdd=apdd)

        # Assert
        # [0,0,0,0,0, 1,1,1,1,1]
        for channel in channel_list:
            assert isinstance(channel, Channel)
        assert len(channel_list) == 10
        for channel in channel_list[0:5]:
            assert channel.channel_id == 0
        for channel in channel_list[5:10]:
            assert channel.channel_id == 1

    def test_build_5channelsand2groupsof3_returnslistoflen6(self):
        # Arrange
        # channel_group ids = [[0,0,0],[1,1,1]]
        test_channel_group_dict_list = self.get_test_channel_group_list(2, 3)
        # channel ids = [0,1,2,3,4]
        test_channel_dict_list = self.get_test_channel_list(5)
        apdd = {
            "ChannelGroups": test_channel_group_dict_list,
            "Channels": test_channel_dict_list,
        }
        # Act
        channel_list = build_channel_list(apdd=apdd)

        # Assert
        # [0,0,0, 1,1,1]
        for channel in channel_list:
            assert isinstance(channel, Channel)
        assert len(channel_list) == 6
        for channel in channel_list[0:3]:
            assert channel.channel_id == 0
        for channel in channel_list[3:6]:
            assert channel.channel_id == 1
