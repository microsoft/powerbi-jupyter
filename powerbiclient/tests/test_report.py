#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

from pytest import raises
import requests_mock
import threading
import time
from unittest.mock import mock_open, patch

from traitlets.traitlets import TraitError
from .. import report
from .utils import create_test_report, ACCESS_TOKEN, REPORT_ID, EMBED_URL, GROUP_ID

PAGE_NAME = 'dummy_page_name'
VISUAL_NAME = 'dummy_visual_name'
VISUAL_DATA = 'dummy_visual_data'
VISUAL_DATA_ROWS = 20
DEFAULT_DATA_ROWS = 10
REPORT_PAGES = ['dummy_report_pages']
PAGE_VISUALS = ['dummy_page_visuals']
REPORT_BOOKMARKS = ['dummy_report_bookmarks']
REPORT_FILTERS = ['dummy_report_filters']

class TestCommAndTraitlets:
    def test_sending_message(self, mock_comm):
        # Arrange
        report = create_test_report()
        report.comm = mock_comm

        new_height = 450
        new_width = 800

        # Act
        report.set_size(new_height, new_width)

        # Assert that comm sends all traitlet changes to frontend
        assert mock_comm.log_send[0][1]['data']['state'] == {
            'container_height': new_height
        }
        assert mock_comm.log_send[1][1]['data']['state'] == {
            'container_width': new_width
        }

    def test_export_visual_data_request_validators(self):
        # Arrange
        report = create_test_report()

        # Act + Assert
        with raises(TraitError):
            report.export_visual_data(PAGE_NAME, VISUAL_NAME, 'number')

    def test_report_filters_request_validators(self):
        # Arrange
        report = create_test_report()

        # Act + Assert
        with raises(TraitError):
            report.update_filters('filter')

    def test_embed_config_validators(self):
        # Arrange
        report = None

        # Act + Assert
        with raises(TraitError):
            report = create_test_report(permissions="INVALID_PERMISSIONS")

        assert report is None


class TestReportConstructor:
    def test_report_constructor(self):
        # Act
        report = create_test_report(embedded=False)

        # Assert
        assert report._embed_config == {
            'type': 'report',
            'accessToken': ACCESS_TOKEN,
            'embedUrl': f"{EMBED_URL}/groups/{GROUP_ID}/reports/{REPORT_ID}",
            'tokenType': 0,
            'viewMode': 0,
            'permissions': None,
            'datasetId': None
        }
        assert report._embedded == False


class TestSettingNewEmbedConfig:
    def test_set_embed_config(self):
        # Arrange
        report = create_test_report()

        new_access_token = "new_dummy_access_token"
        new_embed_url = 'new_dummy_embed_url'

        # Act
        report._set_embed_config(access_token=new_access_token, embed_url=new_embed_url, view_mode=report._embed_config['viewMode'], permissions=report._embed_config['permissions'], dataset_id=report._embed_config['datasetId'])

        # Assert
        assert report._embed_config == {
            'type': 'report',
            'accessToken': new_access_token,
            'embedUrl': new_embed_url,
            'tokenType': 0,
            'viewMode': 0,
            'permissions': None,
            'datasetId': None
        }
        assert report._embedded == False


class TestChangingNewReportSize:
    def test_change_size(self):
        report = create_test_report()

        new_height = 500
        new_width = 900

        report.set_size(new_height, new_width)

        # Assert traitlets are updated
        assert report.container_height == new_height
        assert report.container_width == new_width


class TestEventHandlers:
    def test_throws_for_invalid_event(self):
        # Arrange
        report = create_test_report()
        event_name = 'tileClicked'

        # Act
        def tileClicked_callback():
            pass

        # Act + Assert
        with raises(Exception):
            report.on(event_name, tileClicked_callback)

        # Assert
        assert event_name not in report._registered_event_handlers.keys()
        assert report._observing_events == False

    def test_throws_for_unsupported_event(self):
        # Arrange
        report = create_test_report()
        event_name = 'saved'

        # Act
        def saved_callback():
            pass

        # Act + Assert
        with raises(Exception):
            report.on(event_name, saved_callback)

        # Assert
        assert event_name not in report._registered_event_handlers.keys()
        assert report._observing_events == False

    def test_setting_event_handler(self):
        # Arrange
        report = create_test_report()
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
        report = create_test_report()
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
        report = create_test_report()

        # Act
        # Does not set any handler

        # Assert
        assert 'loaded' not in report._registered_event_handlers

    def test_unsetting_event_handler(self):
        # Arrange
        report = create_test_report()
        event_name = 'loaded'

        # Act
        def loaded_callback():
            pass

        report.on(event_name, loaded_callback)

        # Assert
        assert event_name in report._registered_event_handlers.keys()
        assert report._registered_event_handlers[event_name] == loaded_callback
        assert report._observing_events == True

        # Act
        report.off(event_name)

        # Assert
        assert event_name not in report._registered_event_handlers.keys()


class TestExportData:
    def test_throws_when_not_embedded(self):
        # Arrange
        report = create_test_report(embedded=False)

        # Act + Assert
        with raises(Exception):
            report.export_visual_data('page', 'visual')

    def test_returned_data(self):
        # Arrange
        report = create_test_report()
        # Data sent by frontend (Setting this upfront will prevent extract_data from waiting for data)
        report._visual_data = VISUAL_DATA

        # Act
        returned_data = report.export_visual_data(
            PAGE_NAME, VISUAL_NAME, VISUAL_DATA_ROWS)

        # Assert
        assert returned_data == VISUAL_DATA
        assert report._export_visual_data_request == report.EXPORT_VISUAL_DATA_REQUEST_DEFAULT_STATE
        assert report._visual_data == report.VISUAL_DATA_DEFAULT_STATE


class TestGetPages:
    def test_throws_when_not_embedded(self):
        # Arrange
        report = create_test_report(embedded=False)

        # Act + Assert
        with raises(Exception):
            report.get_pages()

    def test_returned_data(self):
        # Arrange
        report = create_test_report()
        # Data sent by frontend (Setting this upfront will prevent get_pages from waiting for list of pages)
        report._report_pages = REPORT_PAGES

        # Act
        returned_pages = report.get_pages()

        # Assert
        assert returned_pages == REPORT_PAGES
        assert report._get_pages_request == report.GET_PAGES_REQUEST_DEFAULT_STATE
        assert report._report_pages == report.REPORT_PAGES_DEFAULT_STATE


class TestGetVisuals:
    def test_throws_when_not_embedded(self):
        # Arrange
        report = create_test_report(embedded=False)

        # Act + Assert
        with raises(Exception):
            report.get_visuals('page')

    def test_returned_data(self):
        # Arrange
        report = create_test_report()
        # Data sent by frontend (Setting this upfront will prevent get_pages from waiting for list of pages)
        report._page_visuals = PAGE_VISUALS

        # Act
        returned_visuals = report.visuals_on_page(PAGE_NAME)

        # Assert
        assert returned_visuals == PAGE_VISUALS
        assert report._get_visuals_page_name == report.GET_VISUALS_DEFAULT_PAGE_NAME
        assert report._page_visuals == report.PAGE_VISUALS_DEFAULT_STATE


class TestGetBookmarks:
    def test_throws_when_not_embedded(self):
        # Arrange
        report = create_test_report(embedded=False)

        # Act + Assert
        with raises(Exception):
            report.get_bookmarks()

    def test_returned_data(self):
        # Arrange
        report = create_test_report()

        # Data sent by frontend (Setting this upfront will prevent get_bookmarks from waiting for list of bookmarks)
        report._report_bookmarks = REPORT_BOOKMARKS

        # Act
        returned_bookmarks = report.get_bookmarks()

        # Assert
        assert returned_bookmarks == REPORT_BOOKMARKS
        assert report._get_bookmarks_request == report.GET_BOOKMARKS_REQUEST_DEFAULT_STATE
        assert report._report_bookmarks == report.REPORT_BOOKMARKS_DEFAULT_STATE


class TestGetFilters:
    def test_throws_when_not_embedded(self):
        # Arrange
        report = create_test_report(embedded=False)

        # Act + Assert
        with raises(Exception):
            report.get_filters()


    @patch(report.__name__+'.get_ipython')
    @patch(report.__name__+'.ui_events', mock_open())
    def test_returned_data(self, get_ipython_mock):
        get_ipython_mock.return_value = True

        def front_end_mock():
            # Dummy delay to mock front-end
            time.sleep(0.5)

            report._report_filters = REPORT_FILTERS
            report._get_filters_request = False

        # Arrange
        report = create_test_report()

        front_end_mock_thread = threading.Thread(target=front_end_mock)

        # Act
        front_end_mock_thread.start()

        # Assert
        assert report.get_filters() == REPORT_FILTERS
        assert report._get_filters_request == report.GET_FILTERS_REQUEST_DEFAULT_STATE
        assert report._report_filters == report.REPORT_FILTERS_DEFAULT_STATE
