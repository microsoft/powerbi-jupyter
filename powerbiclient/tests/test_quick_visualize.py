#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

from pytest import raises
import unittest
from unittest.mock import patch
from ..quick_visualize import QuickVisualize
from ..report import Report
from .. import authentication
from .utils import create_test_report, ACCESS_TOKEN, REPORT_ID, INITIAL_REPORT_ID


DATASET_CREATE_CONFIG = {
    'locale': 'en-US',
    'tableSchemaList': [{'name': "Table", 'columns': [{'name': "Name", 'dataType': "Text"}]}],
    'data': [{'name': "Table", 'rows': [["test1"], ["test2"]]}]
}
QUICK_CREATE_EMBED_URL = 'https://app.powerbi.com/quickCreate'
REPORT_CREATION_MODE = 'QuickExplore'
EMBED_CONFIG = {
    'accessToken': ACCESS_TOKEN,
    'datasetCreateConfig': DATASET_CREATE_CONFIG,
}

authentication.AUTH = None

def check_if_registered(qv, event_name, callback):
    # Assert
    assert event_name in qv._registered_event_handlers.keys()
    assert qv._registered_event_handlers[event_name] == callback
    assert qv._observing_events == True

class TestQuickVisualizeConstructor:
    def test_quick_visualize_constructor(self):
        # Act
        qv = QuickVisualize(auth=ACCESS_TOKEN, dataset_create_config=DATASET_CREATE_CONFIG)

        # Assert
        assert qv._embed_config == EMBED_CONFIG
        assert qv._embedded == False


class TestComm:
    def test_sending_message(self, mock_comm):
        # Arrange
        qv = QuickVisualize(auth=ACCESS_TOKEN,
                            dataset_create_config=DATASET_CREATE_CONFIG)
        qv.comm = mock_comm

        new_height = 450
        new_width = 800

        # Act
        qv.set_size(new_height, new_width)

        # Assert that comm sends all traitlet changes to frontend
        assert mock_comm.log_send[0][1]['data']['state'] == {
            'container_height': new_height
        }
        assert mock_comm.log_send[1][1]['data']['state'] == {
            'container_width': new_width
        }

class TestUpdateEmbedConfig:
    def test_update_access_token(self):
        # Arrange
        qv = QuickVisualize(auth=ACCESS_TOKEN,
                            dataset_create_config=DATASET_CREATE_CONFIG)
        new_access_token = "new_dummy_access_token"

        # Act
        qv._update_embed_config(access_token=new_access_token)

        # Assert - only access token is updated
        assert qv._embed_config == {
            'accessToken': new_access_token,
            'datasetCreateConfig': DATASET_CREATE_CONFIG,
        }
        assert qv._embedded == False

    def test_update_dataset_create_config(self):
        # Arrange
        qv = QuickVisualize(auth=ACCESS_TOKEN,
                            dataset_create_config=DATASET_CREATE_CONFIG)
        new_dataset_create_config = {
            'locale': 'en-US',
            'tableSchemaList': [{'name': "Table", 'columns': [{'name': "new_Name", 'dataType': "Text"}]}],
            'data': [{'name': "Table", 'rows': [["new_test1"], ["new_test2"]]}]
        }

        # Act
        qv._update_embed_config(
            dataset_create_config=new_dataset_create_config)

        # Assert - only token_expiration is updated
        assert qv._embed_config == {
            'accessToken': ACCESS_TOKEN,
            'datasetCreateConfig': new_dataset_create_config,
        }
        assert qv._embedded == False


class TestChangingNewContainerSize:
    def test_change_size(self):
        # Arrange
        qv = QuickVisualize(auth=ACCESS_TOKEN,
                            dataset_create_config=DATASET_CREATE_CONFIG)

        # Act
        new_height = 500
        new_width = 900

        qv.set_size(new_height, new_width)

        # Assert
        assert qv.container_height == new_height
        assert qv.container_width == new_width

    def test_invalid_height(self):
        # Arrange
        qv = QuickVisualize(auth=ACCESS_TOKEN,
                            dataset_create_config=DATASET_CREATE_CONFIG)

        # Act + Assert
        with raises(Exception):
            qv.set_size(-1, 900)

    def test_invalid_width(self):
        # Arrange
        qv = QuickVisualize(auth=ACCESS_TOKEN,
                            dataset_create_config=DATASET_CREATE_CONFIG)

        # Act + Assert
        with raises(Exception):
            qv.set_size(500, -1)

class TestEventHandlers(unittest.TestCase):
    def test_on_api_throws_for_unsupported_event(self):
        # Arrange
        qv = QuickVisualize(auth=ACCESS_TOKEN,
                            dataset_create_config=DATASET_CREATE_CONFIG)
        event_name = 'tileClicked'

        # Act
        def tileClicked_callback():
            pass

        # Act + Assert
        with raises(Exception):
            qv.on(event_name, tileClicked_callback)

        # Assert
        assert event_name not in qv._registered_event_handlers.keys()
        assert qv._observing_events == False

    def test_off_api_throws_for_unsupported_event(self):
        # Arrange
        qv = QuickVisualize(auth=ACCESS_TOKEN,
                            dataset_create_config=DATASET_CREATE_CONFIG)
        event_name = 'tileClicked'

        # Act + Assert
        with raises(Exception):
            qv.off(event_name)

        # Assert
        assert event_name not in qv._registered_event_handlers.keys()
        assert qv._observing_events == False

    def test_setting_event_handler(self):
        # Arrange
        qv = QuickVisualize(auth=ACCESS_TOKEN,
                            dataset_create_config=DATASET_CREATE_CONFIG)
        event_name = 'loaded'

        # Act
        def loaded_callback():
            pass

        qv.on(event_name, loaded_callback)

        # Assert
        check_if_registered(qv, event_name, loaded_callback)

    def test_setting_event_handler_again(self):
        # Arrange
        qv = QuickVisualize(auth=ACCESS_TOKEN,
                            dataset_create_config=DATASET_CREATE_CONFIG)
        event_name = 'loaded'

        # Act
        def loaded_callback():
            # Dummy callback
            pass

        def loaded_callback2():
            # Dummy callback
            pass

        qv.on(event_name, loaded_callback)
        check_if_registered(qv, event_name, loaded_callback)
        qv.on(event_name, loaded_callback2)

        # Assert
        # Check new handler is registered and old one is unregistered
        check_if_registered(qv, event_name, loaded_callback2)

    def test_not_setting_event_handler(self):
        # Arrange
        qv = QuickVisualize(auth=ACCESS_TOKEN,
                            dataset_create_config=DATASET_CREATE_CONFIG)

        # Act
        # Does not set any handler

        # Assert
        assert qv._registered_event_handlers == qv.REGISTERED_EVENT_HANDLERS_DEFAULT_STATE

    def test_unsetting_event_handler(self):
        # Arrange
        qv = QuickVisualize(auth=ACCESS_TOKEN,
                            dataset_create_config=DATASET_CREATE_CONFIG)
        event_name = 'loaded'

        # Act
        def loaded_callback():
            pass

        qv.on(event_name, loaded_callback)

        # Assert
        check_if_registered(qv, event_name, loaded_callback)

        # Act
        qv.off(event_name)

        # Assert
        assert event_name not in qv._registered_event_handlers.keys()

    def test_unsetting_event_handler_without_setting(self):
        # Arrange
        qv = QuickVisualize(auth=ACCESS_TOKEN,
                            dataset_create_config=DATASET_CREATE_CONFIG)
        event_name = 'loaded'

        # Act + Assert
        qv.off(event_name)

        # Assert
        assert event_name not in qv._registered_event_handlers.keys()
        assert qv._observing_events == False

    @patch.object(QuickVisualize, '_on_saved_report_id_change', return_value=None)
    def test_get_saved_report_throws_error(self, mock_on_saved_report_id_change):
        # Arrange
        qv = QuickVisualize(auth=ACCESS_TOKEN,
                            dataset_create_config=DATASET_CREATE_CONFIG)
        # Assert
        self.assertRaises(Exception, qv.get_saved_report)

    @patch.object(QuickVisualize, '_saved_report', return_value=create_test_report())
    @patch.object(QuickVisualize, '_on_saved_report_id_change', return_value=None)
    def test_get_saved_report_returns_report(self, mock_report, mock_on_saved_report_id_change):
        # Arrange
        qv = QuickVisualize(auth=ACCESS_TOKEN,
                            dataset_create_config=DATASET_CREATE_CONFIG)
        qv._saved_report_id = REPORT_ID

        # Act
        report = qv.get_saved_report().return_value
        embedUrl = report._embed_config['embedUrl']
        reportId = embedUrl.split('/')[-1]

        # Assert
        self.assertIsInstance(report, Report)
        self.assertEqual(reportId, qv._saved_report_id)

    @patch.object(QuickVisualize, '_saved_report', return_value=create_test_report())
    @patch.object(QuickVisualize, '_on_saved_report_id_change', return_value=None)
    def test_get_saved_report_returns_updated_report(self, mock_report, mock_on_saved_report_id_change):
        # Arrange
        qv = QuickVisualize(auth=ACCESS_TOKEN,
                            dataset_create_config=DATASET_CREATE_CONFIG)
        qv._saved_report_id = INITIAL_REPORT_ID

        # Act
        qv._saved_report_id = REPORT_ID
        report = qv.get_saved_report().return_value
        embedUrl = report._embed_config['embedUrl']
        reportId = embedUrl.split('/')[-1]

        # Assert
        self.assertIsInstance(report, Report)
        self.assertEqual(reportId, REPORT_ID)

    @patch.object(QuickVisualize, '_saved_report', return_value=create_test_report())
    @patch.object(QuickVisualize, '_on_saved_report_id_change', return_value=None)
    def test_get_saved_report_returns_report_with_authentication(self, mock_report, mock_on_saved_report_id_change):
        # Arrange
        authentication.AUTH = ACCESS_TOKEN
        qv = QuickVisualize(dataset_create_config=DATASET_CREATE_CONFIG)
        qv._saved_report_id = REPORT_ID

        # Act
        report = qv.get_saved_report().return_value
        embedUrl = report._embed_config['embedUrl']
        reportId = embedUrl.split('/')[-1]

        # Assert
        self.assertIsInstance(report, Report)
        self.assertEqual(reportId, qv._saved_report_id)

        # Reset
        authentication.AUTH = None