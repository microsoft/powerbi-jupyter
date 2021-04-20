#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import pytest

from traitlets.traitlets import TraitError
from ..report import Report

ACCESS_TOKEN = 'dummy_access_token'
EMBED_URL = 'dummy_embed_url'
PAGE_NAME = 'dummy_page_name'
VISUAL_NAME = 'dummy_visual_name'
VISUAL_DATA = 'dummy_visual_data'
VISUAL_DATA_ROWS = 20
DEFAULT_DATA_ROWS = 10
REPORT_PAGES = ['dummy_report_pages']
PAGE_VISUALS = ['dummy_page_visuals']
REPORT_BOOKMARKS = ['dummy_report_bookmarks']


class TestCommAndTraitlets:
    def test_sending_message(self, mock_comm):
        # Arrange
        report = Report(access_token=ACCESS_TOKEN, embed_url=EMBED_URL)
        report._embedded = True
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

    def test_export_visual_data_request_validators(self):
        # Arrange
        report = Report(access_token=ACCESS_TOKEN, embed_url=EMBED_URL)
        report._embedded = True

        # Act + Assert
        with pytest.raises(TraitError):
            report.export_visual_data(PAGE_NAME, VISUAL_NAME, 'number')

    def test_report_filters_request_validators(self):
        # Arrange
        report = Report(access_token=ACCESS_TOKEN, embed_url=EMBED_URL)
        report._embedded = True

        # Act + Assert
        with pytest.raises(TraitError):
            report.update_filters('filter')

    def test_embed_config_validators(self):
        # Arrange
        report = None

        # Act + Assert
        with pytest.raises(TraitError):
            report = Report(access_token=ACCESS_TOKEN, embed_url=EMBED_URL, token_type='AAD')

        assert report is None


class TestReportConstructor:
    def test_report_constructor(self):
        # Act
        report = Report(access_token=ACCESS_TOKEN, embed_url=EMBED_URL)

        # Assert
        assert report._embed_config == {
            'type': 'report',
            'accessToken': ACCESS_TOKEN,
            'embedUrl': EMBED_URL,
            'tokenType': 0,
            'tokenExpiration': 0,
            'viewMode': 0,
            'permissions': 0,
            'datasetId': None
        }
        assert report._embedded == False

    def test_report_constructor_token_type(self):
        # Act
        report = Report(access_token=ACCESS_TOKEN, embed_url=EMBED_URL, token_type=1)

        # Assert
        assert report._embed_config == {
            'type': 'report',
            'accessToken': ACCESS_TOKEN,
            'embedUrl': EMBED_URL,
            'tokenType': 1,
            'tokenExpiration': 0,
            'viewMode': 0,
            'permissions': 0,
            'datasetId': None
        }


class TestSettingNewEmbedConfig:
    def test_set_embed_config(self):
        # Arrange
        report = Report(access_token=ACCESS_TOKEN, embed_url=EMBED_URL)
        # Simulate that report was earlier embedded
        report._embedded = True

        new_access_token = "new_dummy_access_token"
        new_embed_url = 'new_dummy_embed_url'

        # Act
        report._set_embed_config(access_token=new_access_token, embed_url=new_embed_url, view_mode=report._embed_config['viewMode'], permissions=report._embed_config['permissions'], dataset_id=report._embed_config['datasetId'], token_type=report._embed_config['tokenType'], token_expiration=report._embed_config['tokenExpiration'])

        # Assert
        assert report._embed_config == {
            'type': 'report',
            'accessToken': new_access_token,
            'embedUrl': new_embed_url,
            'tokenType': 0,
            'tokenExpiration': 0,
            'viewMode': 0,
            'permissions': 0,
            'datasetId': None
        }
        assert report._embedded == False


class TestChangingNewReportSize:
    def test_change_size(self):
        report = Report(access_token=ACCESS_TOKEN, embed_url=EMBED_URL)
        report._embedded = True

        new_height = 500
        new_width = 900

        report.set_dimensions(new_height, new_width)

        # Assert traitlets are updated
        assert report.container_height == new_height
        assert report.container_width == new_width


class TestEventHandlers:
    def test_throws_for_invalid_event(self):
        # Arrange
        report = Report(access_token=ACCESS_TOKEN, embed_url=EMBED_URL)
        report._embedded = True
        event_name = 'tileClicked'

        # Act
        def tileClicked_callback():
            pass

        # Act + Assert
        with pytest.raises(Exception):
            report.on(event_name, tileClicked_callback)

        # Assert
        assert event_name not in report._registered_event_handlers.keys()
        assert report._observing_events == False

    def test_throws_for_unsupported_event(self):
        # Arrange
        report = Report(access_token=ACCESS_TOKEN, embed_url=EMBED_URL)
        report._embedded = True
        event_name = 'saved'

        # Act
        def saved_callback():
            pass

        # Act + Assert
        with pytest.raises(Exception):
            report.on(event_name, saved_callback)

        # Assert
        assert event_name not in report._registered_event_handlers.keys()
        assert report._observing_events == False

    def test_setting_event_handler(self):
        # Arrange
        report = Report(access_token=ACCESS_TOKEN, embed_url=EMBED_URL)
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
        report = Report(access_token=ACCESS_TOKEN, embed_url=EMBED_URL)
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
        report = Report(access_token=ACCESS_TOKEN, embed_url=EMBED_URL)

        # Act
        # Does not set any handler

        # Assert
        assert 'loaded' not in report._registered_event_handlers


class TestExportData:
    def test_throws_when_not_embedded(self):
        # Arrange
        report = Report(access_token=ACCESS_TOKEN, embed_url=EMBED_URL)
        report._embedded = False

        # Act + Assert
        with pytest.raises(Exception):
            report.export_visual_data('page', 'visual')

    def test_returned_data(self):
        # Arrange
        report = Report(access_token=ACCESS_TOKEN, embed_url=EMBED_URL)
        # Data sent by frontend (Setting this upfront will prevent extract_data from waiting for data)
        report._visual_data = VISUAL_DATA
        report._embedded = True

        # Act
        returned_data = report.export_visual_data(PAGE_NAME, VISUAL_NAME, VISUAL_DATA_ROWS)

        # Assert
        assert returned_data == VISUAL_DATA
        assert report._export_visual_data_request == report.EXPORT_VISUAL_DATA_REQUEST_DEFAULT_STATE
        assert report._visual_data == report.VISUAL_DATA_DEFAULT_STATE


class TestGetPages:
    def test_throws_when_not_embedded(self):
        # Arrange
        report = Report(access_token=ACCESS_TOKEN, embed_url=EMBED_URL)
        report._embedded = False

        # Act + Assert
        with pytest.raises(Exception):
            report.get_pages()

    def test_returned_data(self):
        # Arrange
        report = Report(access_token=ACCESS_TOKEN, embed_url=EMBED_URL)
        # Data sent by frontend (Setting this upfront will prevent get_pages from waiting for list of pages)
        report._report_pages = REPORT_PAGES
        report._embedded = True

        # Act
        returned_pages = report.get_pages()

        # Assert
        assert returned_pages == REPORT_PAGES
        assert report._get_pages_request == report.GET_PAGES_REQUEST_DEFAULT_STATE
        assert report._report_pages == report.REPORT_PAGES_DEFAULT_STATE


class TestGetVisuals:
    def test_throws_when_not_embedded(self):
        # Arrange
        report = Report(access_token=ACCESS_TOKEN, embed_url=EMBED_URL)
        report._embedded = False

        # Act + Assert
        with pytest.raises(Exception):
            report.get_visuals('page')

    def test_returned_data(self):
        # Arrange
        report = Report(access_token=ACCESS_TOKEN, embed_url=EMBED_URL)
        # Data sent by frontend (Setting this upfront will prevent get_pages from waiting for list of pages)
        report._page_visuals = PAGE_VISUALS
        report._embedded = True

        # Act
        returned_visuals = report.visuals_on_page(PAGE_NAME)

        # Assert
        assert returned_visuals == PAGE_VISUALS
        assert report._get_visuals_page_name == report.GET_VISUALS_DEFAULT_PAGE_NAME
        assert report._page_visuals == report.PAGE_VISUALS_DEFAULT_STATE


class TestGetBookmarks:
    def test_throws_when_not_embedded(self):
        # Arrange
        report = Report(access_token=ACCESS_TOKEN, embed_url=EMBED_URL)
        report._embedded = False

        # Act + Assert
        with pytest.raises(Exception):
            report.get_bookmarks()

    def test_returned_data(self):
        # Arrange
        report = Report(access_token=ACCESS_TOKEN, embed_url=EMBED_URL)

        # Data sent by frontend (Setting this upfront will prevent get_bookmarks from waiting for list of bookmarks)
        report._report_bookmarks = REPORT_BOOKMARKS
        report._embedded = True

        # Act
        returned_bookmarks = report.get_bookmarks()

        # Assert
        assert returned_bookmarks == REPORT_BOOKMARKS
        assert report._get_bookmarks_request == report.GET_BOOKMARKS_REQUEST_DEFAULT_STATE
        assert report._report_bookmarks == report.REPORT_BOOKMARKS_DEFAULT_STATE
