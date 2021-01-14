#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Microsoft.
# Distributed under the terms of the Modified BSD License.

import pytest

from ..report import Report

ACCESS_TOKEN = 'dummy_access_token'
EMBED_URL = 'dummy_embed_url'
PAGE_NAME = 'dummy_page_name'
VISUAL_NAME = 'dummy_visual_name'
VISUAL_DATA = 'dummy_visual_data'
VISUAL_DATA_ROWS = 20
DEFAULT_DATA_ROWS = 10


class TestCommAndTraitlets:
    def test_sending_message(self, mock_comm):
        # Arrange
        report = Report(ACCESS_TOKEN, EMBED_URL)
        report.comm = mock_comm

        new_height = 450
        new_width = 800

        # Act
        report.set_dimensions(new_height, new_width)

        # Assert that comm sends all traitlet changes to frontend
        assert mock_comm.log_send[0][1]['data']['state'] == {
            'container_height': new_height
        }
        assert mock_comm.log_send[1][1]['data']['state'] == {
            'container_width': new_width
        }


class TestReportConstructor:
    def test_report_constructor(self):
        # Act
        report = Report(ACCESS_TOKEN, EMBED_URL)

        # Assert
        assert report.embed_config == {
            'type': 'report',
            'accessToken': ACCESS_TOKEN,
            'embedUrl': EMBED_URL,
            'tokenType': 0
        }
        assert report._embedded == False

    def test_report_constructor_token_type(self):
        # Act
        report = Report(ACCESS_TOKEN, EMBED_URL, token_type=1)

        # Assert
        assert report.embed_config == {
            'type': 'report',
            'accessToken': ACCESS_TOKEN,
            'embedUrl': EMBED_URL,
            'tokenType': 1
        }


class TestSettingNewEmbedConfig:
    def test_set_embed_config(self):
        # Arrange
        report = Report(ACCESS_TOKEN, EMBED_URL)
        # Simulate that report was earlier embedded
        report._embedded = True

        new_access_token = "new_dummy_access_token"
        new_embed_url = 'new_dummy_embed_url'

        # Act
        report.set_embed_config(new_access_token, new_embed_url)

        # Assert
        assert report.embed_config == {
            'type': 'report',
            'accessToken': new_access_token,
            'embedUrl': new_embed_url,
            'tokenType': 0
        }
        assert report._embedded == False


class TestChangingNewReportSize:
    def test_change_size(self):
        report = Report(ACCESS_TOKEN, EMBED_URL)

        new_height = 500
        new_width = 900

        report.set_dimensions(new_height, new_width)

        # Assert traitlets are updated
        assert report.container_height == new_height
        assert report.container_width == new_width


class TestEventHandlers:
    def test_setting_event_handler(self):
        # Arrange
        report = Report(ACCESS_TOKEN, EMBED_URL)
        report._embedded = True
        event_name = 'loaded'

        # Act
        def loaded_callback():
            pass

        report.on(event_name, loaded_callback)

        # Assert
        assert event_name in report._registered_event_handlers.keys()
        assert report._registered_event_handlers[event_name] == loaded_callback
        assert report._observing_events == True

    def test_setting_event_handler_again(self):
        # Arrange
        report = Report(ACCESS_TOKEN, EMBED_URL)
        report._embedded = True
        event_name = 'loaded'

        # Act
        def loaded_callback():
            # Dummy callback
            pass

        def loaded_callback2():
            # Dummy callback
            pass

        report.on(event_name, loaded_callback)
        report.on(event_name, loaded_callback2)

        # Assert
        assert event_name in report._registered_event_handlers.keys()
        # Check new handler is registered and old one is unregistered
        assert report._registered_event_handlers[event_name] == loaded_callback2
        assert report._observing_events == True

    def test_not_setting_event_handler(self):
        # Arrange
        report = Report(ACCESS_TOKEN, EMBED_URL)

        # Act
        # Does not set any handler

        # Assert
        assert 'loaded' not in report._registered_event_handlers


class TestExtractData:
    def test_throws_when_not_embedded(self):
        # Arrange
        report = Report(ACCESS_TOKEN, EMBED_URL)
        report._embedded = False

        # Act + Assert
        with pytest.raises(Exception):
            report.extract_data('page', 'visual')

    def test_returned_data(self):
        # Arrange
        report = Report(ACCESS_TOKEN, EMBED_URL)
        # Data sent by frontend (Setting this upfront will prevent extract_data from waiting for data)
        report.visual_data = VISUAL_DATA
        report._embedded = True

        # Act
        returned_data = report.extract_data(PAGE_NAME, VISUAL_NAME, VISUAL_DATA_ROWS)

        # Assert
        assert returned_data == VISUAL_DATA
        assert report.extract_data_request == report.EXTRACT_DATA_REQUEST_DEFAULT_STATE
        assert report.visual_data == report.VISUAL_DATA_DEFAULT_STATE
