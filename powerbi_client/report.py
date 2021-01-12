#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Microsoft.

"""
TODO: Add module docstring
"""

import time
from asyncio import Future, ensure_future

from ipywidgets import DOMWidget
from jupyter_ui_poll import ui_events
from traitlets import Bool, Dict, Float, Unicode, observe

from ._frontend import module_name, module_version


class Report(DOMWidget):
    """PowerBI report embedding widget"""

    # Name of the widget view class in front-end
    _view_name = Unicode('ReportView').tag(sync=True)

    # Name of the widget model class in front-end
    _model_name = Unicode('ReportModel').tag(sync=True)

    # Name of the front-end module containing widget view
    _view_module = Unicode('powerbi-client-frontend').tag(sync=True)

    # Name of the front-end module containing widget model
    _model_module = Unicode('powerbi-client-frontend').tag(sync=True)

    # Version of the front-end module containing widget view
    _view_module_version = Unicode('^0.1.0').tag(sync=True)

    # Version of the front-end module containing widget model
    _model_module_version = Unicode('^0.1.0').tag(sync=True)

    # Default values for widget traits
    VISUAL_DATA_DEFAULT_STATE = ''
    EXTRACT_DATA_REQUEST_DEFAULT_STATE = {}
    REGISTERED_EVENT_HANDLERS_DEFAULT_STATE = {}
    EVENT_DATA_DEFAULT_STATE = {
        'event_name': None,
        'event_details': None
    }

    # Widget specific properties.
    # Widget properties are defined as traitlets. Any property tagged with `sync=True`
    # is automatically synced to the frontend *any* time it changes in Python.
    # It is synced back to Python from the frontend *any* time the model is touched in frontend.

    # TODO: Add trait validation
    embed_config = Dict(None).tag(sync=True)
    _embedded = Bool(False).tag(sync=True)

    container_height = Float(0).tag(sync=True)
    container_width = Float(0).tag(sync=True)

    # TODO: Add validation
    extract_data_request = Dict(None).tag(sync=True)
    visual_data = Unicode(VISUAL_DATA_DEFAULT_STATE).tag(sync=True)

    _event_data = Dict(EVENT_DATA_DEFAULT_STATE).tag(sync=True)

    # Methods
    def __init__(self, access_token, embed_url, token_type=0, **kwargs):
        # Tells if Power BI events are being observed
        self._observing_events = False

        # Registered Power BI event handlers methods
        self._registered_event_handlers = self.REGISTERED_EVENT_HANDLERS_DEFAULT_STATE

        self.set_embed_config(access_token, embed_url, token_type)

        # Init parent class DOMWidget
        super(Report, self).__init__(**kwargs)

    def set_embed_config(self, access_token, embed_url, token_type=0):
        """
        TODO: Add docstring
        """
        self.embed_config = {
            'type': 'report',
            'accessToken': access_token,
            'embedUrl': embed_url,
            'tokenType': token_type
        }
        self._embedded = False

    def set_dimensions(self, container_height, container_width):
        """Set width and height of Power BI report in px

        Args:
            container_height (number): report height
            container_width (number): report width
        """
        self.container_height = container_height
        self.container_width = container_width

    def extract_data(self, page_name, visual_name, rows=10):
        """Returns the data of given visual of the embedded Power BI report

        Args:
            page_name (string): Page name of the embedded report
            visual_name (string): Visual's unique name 
            rows (int, optional): Number of rows of data. Defaults to 10.

        Returns:
            string: visual's exported data
        """
        if self._embedded == False:
            raise Exception("Report is not embedded")

        # Start exporting data on client side
        self.extract_data_request = {
            'pageName': page_name,
            'visualName': visual_name,
            'rows': rows
        }

        PROCESS_EVENTS_ITERATION = 3    # Process upto n UI events per iteration
        POLLING_INTERVAL = 0.5  # Check for UI every n seconds

        # Wait for client-side to send visual data
        with ui_events() as ui_poll:
            # While visual data is not updated
            while self.visual_data == self.VISUAL_DATA_DEFAULT_STATE:
                ui_poll(PROCESS_EVENTS_ITERATION)
                time.sleep(POLLING_INTERVAL)

        exported_data = self.visual_data

        # Reset the extract_data_request and visual_data's value
        self.extract_data_request = self.EXTRACT_DATA_REQUEST_DEFAULT_STATE
        self.visual_data = self.VISUAL_DATA_DEFAULT_STATE

        return exported_data

    def wait_for_change(self, value):
        """
        TODO: Add docstring
        """
        future = Future()

        # Callback for processing exported_data
        def get_value(change):
            future.set_result(change.new)
            self.unobserve(get_value, value)

        self.observe(get_value, value)
        return future

    def on(self, event, callback):
        """Register a callback to execute when the report emits the target event
        Parameters

        Args:
            event (string): Name of Power BI event (eg. 'loaded', 'rendered', 'error')
            callback (function): User defined function. Callback function is invoked with event details as parameter
        """
        self._registered_event_handlers[event] = callback

        def get_event_data(change):

            event_data = change.new
            event_name = event_data['event_name']
            event_details = event_data['event_details']

            # Do not invoke callback when _event_data trait is reset
            if event_name is None:
                return

            # Check if a handler is registered for the current event
            if event_name not in self._registered_event_handlers:
                return

            event_handler = self._registered_event_handlers[event_name]
            event_handler(event_details)

            # Reset the _event_data trait, so as to receive next event
            self._event_data = self.EVENT_DATA_DEFAULT_STATE

        # Check if already observing events
        if not self._observing_events:

            # Prevents calling DOMWidget.observe() again
            self._observing_events = True

            # Start observing Power BI events
            self.observe(get_event_data, '_event_data')
