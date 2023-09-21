#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

"""
Power BI quick visualization widget
"""

from ipywidgets import DOMWidget
from traitlets import Bool, Dict, Float, HasTraits, Unicode, TraitError, validate, observe

from . import authentication
from .report import Report
from ._version import __version__
from .utils import MODULE_NAME, is_dataset_create_config_valid, get_access_token_details


class QuickVisualize(DOMWidget, HasTraits):
    """Power BI quick visualization widget"""

    # Name of the widget view class in front-end
    _view_name = Unicode('QuickVisualizeView').tag(sync=True)

    # Name of the widget model class in front-end
    _model_name = Unicode('QuickVisualizeModel').tag(sync=True)

    # Name of the front-end module containing widget view
    _view_module = Unicode(MODULE_NAME).tag(sync=True)

    # Name of the front-end module containing widget model
    _model_module = Unicode(MODULE_NAME).tag(sync=True)

    # Version of the front-end module containing widget view
    _view_module_version = Unicode(__version__).tag(sync=True)

    # Version of the front-end module containing widget model
    _model_module_version = Unicode(__version__).tag(sync=True)

    # Default values for widget traits
    EMBED_CONFIG_DEFAULT_STATE = {
        'accessToken': None,
        'datasetCreateConfig': None,
    }
    REGISTERED_EVENT_HANDLERS_DEFAULT_STATE = {}
    EVENT_DATA_DEFAULT_STATE = {
        'event_name': None,
        'event_details': None
    }
    INIT_ERROR_DEFAULT_STATE = ''
    SAVED_REPORT_ID_DEFAULT_STATE = ''
    TOKEN_EXPIRED_DEFAULT_STATE = False

    # Supported events list for quick_visualize widget
    SUPPORTED_EVENTS = ['loaded', 'rendered', 'saved']

    # Authentication object
    _auth = None

    # Widget specific properties.
    # Widget properties are defined as traitlets. Any property tagged with `sync=True`
    # is automatically synced to the frontend *any* time it changes in Python.
    # It is synced back to Python from the frontend *any* time the model is touched in frontend.

    _embed_config = Dict(EMBED_CONFIG_DEFAULT_STATE).tag(sync=True)
    _embedded = Bool(False).tag(sync=True)
    _token_expired = Bool(TOKEN_EXPIRED_DEFAULT_STATE).tag(sync=True)
    _event_data = Dict(EVENT_DATA_DEFAULT_STATE).tag(sync=True)
    _init_error = Unicode(INIT_ERROR_DEFAULT_STATE).tag(sync=True)
    _saved_report_id = Unicode(SAVED_REPORT_ID_DEFAULT_STATE).tag(sync=True)
    _saved_report: Report = None
    container_height = Float(0).tag(sync=True)
    container_width = Float(0).tag(sync=True)

    @validate('_embed_config')
    def _valid_embed_config(self, proposal):
        if proposal['value'] == self.EMBED_CONFIG_DEFAULT_STATE:
            return proposal['value']
        if ((type(proposal['value']['accessToken']) is not str) or (proposal['value']['accessToken'] == '')):
            raise TraitError('Invalid accessToken ',
                             proposal['value']['accessToken'])
        if (not is_dataset_create_config_valid(proposal['value']['datasetCreateConfig'])):
            raise TraitError('Invalid datasetCreateConfig ',
                             proposal['value']['datasetCreateConfig'])
        return proposal['value']

    # Raise exception for errors when embedding the Power BI quick visualization
    @observe('_init_error')
    def _on_error(self, change):
        if (change['new'] is not self.INIT_ERROR_DEFAULT_STATE):
            self._init_error = self.INIT_ERROR_DEFAULT_STATE
            raise Exception(change['new'])

    # Methods
    def __init__(self, dataset_create_config, auth=None, **kwargs):
        """Create an instance of Quick Visualization in Power BI

        Args:
            dataset_create_config (object): Required.
                A dict representing the data used to create the report, formatted as IDatasetCreateConfiguration
                (See: https://learn.microsoft.com/en-us/javascript/api/overview/powerbi/embed-quick-report#step-11---create-a-dataset-without-a-data-source)

            auth (string or object): Optional.
                We have 3 authentication options to embed Power BI quick visualization:
                 - Access token (string)
                 - Authentication object (object) - instance of AuthenticationResult (DeviceCodeLoginAuthentication or InteractiveLoginAuthentication)
                 - If not provided, Power BI user will be authenticated using Device Flow authentication

        Returns:
            object: QuickVisualize object
        """

        self.observe(self._on_saved_report_id_change, '_saved_report_id')

        access_token = get_access_token_details(
            powerbi_widget=QuickVisualize, auth=auth)
        self._update_embed_config(
            access_token=access_token, dataset_create_config=dataset_create_config)

        # Registered Power BI event handlers methods
        self._registered_event_handlers = dict(
            self.REGISTERED_EVENT_HANDLERS_DEFAULT_STATE)

        # Tells if Power BI events are being observed
        self._observing_events = False

        self.observe(self._update_access_token, '_token_expired')

        # Init parent class DOMWidget
        super(QuickVisualize, self).__init__(**kwargs)

    def _on_saved_report_id_change(self, change):
        """update saved report object when saved report id changes"""
        if self._saved_report is None or (self._saved_report_id != change['old']):
            if authentication.AUTH:
                self._saved_report = Report(report_id=self._saved_report_id)
            else:
                self._saved_report = Report(report_id=self._saved_report_id, auth=self._auth)

    def _update_access_token(self, change):
        if change.new == True:
            self._token_expired = bool(self.TOKEN_EXPIRED_DEFAULT_STATE)
            if not self._auth:
                raise Exception(
                    "Token expired and authentication context not found")

            try:
                access_token = self._auth.get_access_token(force_refresh=True)
            except Exception as ex:
                error_message = f"Refresh token failed.\nDetails: {ex}"
                Exception(error_message)

            self._update_embed_config(access_token=access_token)

    def set_access_token(self, access_token):
        """Set an access token for the Power BI quick visualization

        Args:
            access_token (string)
        """
        if not access_token:
            raise Exception("Access token cannot be empty")
        self._update_embed_config(access_token=access_token)

    def _update_embed_config(self, access_token=None, dataset_create_config=None):
        """
            Set embed configuration parameters of Power BI quick visualization
        """
        self._embed_config = {
            'accessToken': access_token or self._embed_config['accessToken'],
            'datasetCreateConfig': dataset_create_config or self._embed_config['datasetCreateConfig'],
        }
        self._embedded = False

    def _is_event_supported(self, event):
        # Check if event is one of the QuickVisualize.SUPPORTED_EVENTS list
        if event not in self.SUPPORTED_EVENTS:
            raise Exception(f"'{event}' event is not supported")

    def get_saved_report(self):
        """Returns the saved report associated with this QuickVisualize instance.

        Returns:
            Report: The saved report object.

        Raises:
            Exception: If no saved report is found.
        """
        if self._saved_report_id == self.SAVED_REPORT_ID_DEFAULT_STATE:
            raise Exception("No saved report found")
        return self._saved_report

    def on(self, event, callback):
        """Register a callback to execute when the Power BI quick visualization emits the target event

        Args:
            event (string): Name of Power BI event (supported events: 'loaded', 'rendered', 'saved')
            callback (function): User defined function. Callback function is invoked with event details as parameter
        """

        self._is_event_supported(event)

        if callback is None:
            raise Exception('callback cannot be None')

        if not callable(callback):
            raise Exception('callback must be a function')

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
            self._event_data = dict(self.EVENT_DATA_DEFAULT_STATE)

        if not self._observing_events:

            # Prevents calling DOMWidget.observe() again
            self._observing_events = True

            # Start observing Power BI events
            self.observe(get_event_data, '_event_data')

    def off(self, event):
        """Unregisters a callback on target event

        Args:
            event (string): Name of Power BI event (supported events: 'loaded', 'rendered', 'saved')
        """
        # Check if the passed event is supported by Power BI quick visualization
        self._is_event_supported(event)

        # Remove handler if registered for the current event
        if event in self._registered_event_handlers:
            self._registered_event_handlers.pop(event)

    def set_size(self, container_height, container_width):
        """Set height and width of Power BI quick visualization in px

        Args:
            container_height (float)
            container_width (float)
        """
        if container_height < 0:
            raise TraitError('Invalid height {0}'.format(container_height))
        if container_width < 0:
            raise TraitError('Invalid width {0}'.format(container_width))

        self.container_height = container_height
        self.container_width = container_width
