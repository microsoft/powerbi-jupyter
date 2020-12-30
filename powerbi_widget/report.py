#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Microsoft.

"""
TODO: Add module docstring
"""

from asyncio import Future, ensure_future

from ipywidgets import DOMWidget
from traitlets import Bool, Dict, Float, Unicode, observe

from ._frontend import module_name, module_version


class Report(DOMWidget):
    """PowerBI report embedding widget"""

    # Name of the widget view class in front-end
    _view_name = Unicode('ReportView').tag(sync=True)

    # Name of the widget model class in front-end
    _model_name = Unicode('ReportModel').tag(sync=True)

    # Name of the front-end module containing widget view
    _view_module = Unicode('powerbi-widget-client').tag(sync=True)

    # Name of the front-end module containing widget model
    _model_module = Unicode('powerbi-widget-client').tag(sync=True)

    # Version of the front-end module containing widget view
    _view_module_version = Unicode('^0.1.0').tag(sync=True)

    # Version of the front-end module containing widget model
    _model_module_version = Unicode('^0.1.0').tag(sync=True)

    # Widget specific properties.
    # Widget properties are defined as traitlets. Any property tagged with `sync=True`
    # is automatically synced to the frontend *any* time it changes in Python.
    # It is synced back to Python from the frontend *any* time the model is touched.

    _embedded = Bool(False).tag(sync=True)

    embed_config = Dict(None).tag(sync=True)

    container_height = Float(None).tag(sync=True)

    container_width = Float(None).tag(sync=True)

    visual_data = Unicode('').tag(sync=True)

    # TODO: Add validation
    extract_data_request = Dict(None).tag(sync=True)

    # Methods
    def __init__(self, access_token, embed_url, token_type=0, **kwargs):
        self.embed_config = {
            'type': 'report',
            'accessToken': access_token,
            'embedUrl': embed_url,
            'tokenType': token_type
        }
        self.container_height = 0
        self.container_width = 0
        self._embedded = False

        super(Report, self).__init__(**kwargs)

    def set_embed_config(self, access_token, embed_url, token_type=0):
        self.embed_config = {
            'type': 'report',
            'accessToken': access_token,
            'embedUrl': embed_url,
            'tokenType': token_type
        }
        self._embedded = False

    def set_dimensions(self, container_height, container_width):
        self.container_height = container_height
        self.container_width = container_width

    def extract_data(self, page_name, visual_name, rows=10):
        """Returns the data of given visual of the embedded Power BI report

        Args:
            page_name (string): Page name of the embedded report
            visual_name (string): Visual's unique name 
            rows (int, optional): Number of rows of data. Defaults to 10.

        Returns:
            Task: async task which results in extracted visual data
            # TODO: Return data directly
        """
        # Starts executing the export data task
        return ensure_future(self._extract_data(page_name, visual_name, rows))

    async def _extract_data(self, page_name, visual_name, rows=10):
        if self._embedded == False:
            raise Exception("Report is not embedded")

        # Start exporting data on client side
        self.extract_data_request = {
            'pageName': page_name,
            'visualName': visual_name,
            'rows': rows
        }

        # TODO: Wait for the future to be done and return its result
        exported_data_task = await self.wait_for_change('visual_data')

        # Reset the extract_data_request and visual_data's value
        self.extract_data_request = {}
        self.visual_data = ''

        # Return the asyncio.task instance
        return exported_data_task

    def wait_for_change(self, value):

        future = Future()

        # Callback for processing exported_data
        def get_value(change):
            future.set_result(change.new)
            self.unobserve(get_value, value)

        self.observe(get_value, value)
        return future
