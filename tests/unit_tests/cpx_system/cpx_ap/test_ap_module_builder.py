"""Contains tests for ApModule class"""

from unittest.mock import Mock
import pytest

from cpx_io.cpx_system.cpx_ap.ap_module_builder import ApModuleBuilder, ChannelGroup


class TestApModuleBuilder:
    "Test ApModuleBuilder"

    def test_build_channel_group(self):
        """Test configure"""
        # Arrange
        ap_module_builder = ApModuleBuilder()
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
        channel_group = ap_module_builder.build_channel_group(channel_group_dict)

        # Assert
        assert isinstance(channel_group, ChannelGroup)
        assert channel_group.channel_group_id == channel_group_id
        assert channel_group.channels == channels
        assert channel_group.name == name
        assert channel_group.parameter_group_ids == parameter_group_ids
