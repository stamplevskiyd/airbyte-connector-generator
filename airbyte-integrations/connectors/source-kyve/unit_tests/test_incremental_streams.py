#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from pytest import fixture
from source_kyve.source import KYVEStream as IncrementalKyveStream

from airbyte_cdk.models import SyncMode

from . import config, pool_data


@fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(IncrementalKyveStream, "path", "v0/example_endpoint")
    mocker.patch.object(IncrementalKyveStream, "primary_key", "test_primary_key")
    mocker.patch.object(IncrementalKyveStream, "__abstractmethods__", set())


def test_cursor_field(patch_incremental_base_class):
    stream = IncrementalKyveStream(config, pool_data)
    # TODO: replace this with your expected cursor field
    expected_cursor_field = "offset"
    assert stream.cursor_field == expected_cursor_field


def test_get_updated_state(patch_incremental_base_class):
    stream = IncrementalKyveStream(config, pool_data)
    # TODO: replace this with your input parameters
    inputs = {"current_stream_state": None, "latest_record": None}
    # TODO: replace this with your expected updated stream state
    expected_state = {}
    assert stream.get_updated_state(**inputs) == expected_state


def test_stream_slices(patch_incremental_base_class):
    stream = IncrementalKyveStream(config, pool_data)
    # TODO: replace this with your input parameters
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": [], "stream_state": {}}
    # TODO: replace this with your expected stream slices list
    expected_stream_slice = [None]
    assert stream.stream_slices(**inputs) == expected_stream_slice


def test_supports_incremental(patch_incremental_base_class, mocker):
    mocker.patch.object(IncrementalKyveStream, "cursor_field", "dummy_field")
    stream = IncrementalKyveStream(config, pool_data)
    assert stream.supports_incremental


def test_source_defined_cursor(patch_incremental_base_class):
    stream = IncrementalKyveStream(config, pool_data)
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(patch_incremental_base_class):
    stream = IncrementalKyveStream(config, pool_data)
    # TODO: replace this with your expected checkpoint interval
    expected_checkpoint_interval = None
    assert stream.state_checkpoint_interval == expected_checkpoint_interval
