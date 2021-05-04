#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

"""
Embeds Power BI Report
"""

import time
import requests

from IPython import get_ipython
from ipywidgets import DOMWidget
from jupyter_ui_poll import ui_events
from traitlets import Bool, Dict, Float, Unicode, List, TraitError, validate

from ._frontend import module_name, module_version
from .models import Permissions, EmbedMode, TokenType, ExportDataType, EmbedType

from .authentication import DeviceCodeLoginAuthentication, CREATE_REPORT_SCOPES


class Report(DOMWidget):
    """PowerBI report embedding widget"""

    # Name of the widget view class in front-end
    _view_name = Unicode('ReportView').tag(sync=True)

    # Name of the widget model class in front-end
    _model_name = Unicode('ReportModel').tag(sync=True)

    # Name of the front-end module containing widget view
    _view_module = Unicode('powerbi-jupyter-client').tag(sync=True)

    # Name of the front-end module containing widget model
    _model_module = Unicode('powerbi-jupyter-client').tag(sync=True)

    # Version of the front-end module containing widget view
    _view_module_version = Unicode('^0.1.0').tag(sync=True)

    # Version of the front-end module containing widget model
    _model_module_version = Unicode('^0.1.0').tag(sync=True)

    # Default values for widget traits
    EMBED_CONFIG_DEFAULT_STATE = {
        'type': 'report',
        'accessToken': None,
        'embedUrl': None,
        'tokenType': None,
        'tokenExpiration': None,
        'viewMode': None,
        'permissions': None,
        'datasetId': None
    }
    VISUAL_DATA_DEFAULT_STATE = ''
    EXPORT_VISUAL_DATA_REQUEST_DEFAULT_STATE = {
        'pageName': None,
        'visualName': None,
        'rows': None,
        'exportDataType': None
    }
    REGISTERED_EVENT_HANDLERS_DEFAULT_STATE = {}
    EVENT_DATA_DEFAULT_STATE = {
        'event_name': None,
        'event_details': None
    }
    GET_FILTERS_REQUEST_DEFAULT_STATE = False
    REPORT_FILTERS_DEFAULT_STATE = []
    REPORT_FILTER_REQUEST_DEFAULT_STATE = {
        'filters': [],
        'request_completed': True
    }
    GET_PAGES_REQUEST_DEFAULT_STATE = False
    REPORT_PAGES_DEFAULT_STATE = []
    GET_VISUALS_DEFAULT_PAGE_NAME = ''
    PAGE_VISUALS_DEFAULT_STATE = []
    GET_BOOKMARKS_REQUEST_DEFAULT_STATE = False
    REPORT_BOOKMARKS_DEFAULT_STATE = []
    REPORT_BOOKMARK_DEFAULT_NAME = ''
    TOKEN_EXPIRED_DEFAULT_STATE = False
    CLIENT_ERROR_DEFAULT_STATE = ''

    # Other constants
    REPORT_NOT_EMBEDDED_MESSAGE = "Power BI report is not embedded"

    # Process upto n UI events per iteration
    PROCESS_EVENTS_ITERATION = 3

    # Check for UI every n seconds
    POLLING_INTERVAL = 0.5

    # Authentication object
    _auth = None

    # Allowed events list for Power BI report
    ALLOWED_EVENTS = ['loaded', 'saved', 'rendered', 'saveAsTriggered', 'error', 'dataSelected', 'buttonClicked', 'filtersApplied', 'pageChanged', 'commandTriggered', 'swipeStart', 'swipeEnd', 'bookmarkApplied', 'dataHyperlinkClicked', 'visualRendered', 'visualClicked', 'selectionChanged']

    # Supported events list for Report widget
    SUPPORTED_EVENTS = ['loaded', 'rendered', 'error']

    # Default request body for generate token API
    DEFAULT_EMBED_TOKEN_REQUEST_BODY = { "accessLevel": "View" }

    # Widget specific properties.
    # Widget properties are defined as traitlets. Any property tagged with `sync=True`
    # is automatically synced to the frontend *any* time it changes in Python.
    # It is synced back to Python from the frontend *any* time the model is touched in frontend.

    _embed_config = Dict(EMBED_CONFIG_DEFAULT_STATE).tag(sync=True)
    _embedded = Bool(False).tag(sync=True)

    container_height = Float(0).tag(sync=True)
    container_width = Float(0).tag(sync=True)

    _export_visual_data_request = Dict(None).tag(sync=True)
    _visual_data = Unicode(VISUAL_DATA_DEFAULT_STATE).tag(sync=True)

    _event_data = Dict(EVENT_DATA_DEFAULT_STATE).tag(sync=True)

    _get_filters_request = Bool(GET_FILTERS_REQUEST_DEFAULT_STATE).tag(sync=True)
    _report_filters = List(REPORT_FILTERS_DEFAULT_STATE).tag(sync=True)
    _report_filters_request = Dict(REPORT_FILTER_REQUEST_DEFAULT_STATE).tag(sync=True)

    _get_pages_request = Bool(GET_PAGES_REQUEST_DEFAULT_STATE).tag(sync=True)
    _report_pages = List(REPORT_PAGES_DEFAULT_STATE).tag(sync=True)

    _get_visuals_page_name = Unicode(GET_VISUALS_DEFAULT_PAGE_NAME).tag(sync=True)
    _page_visuals = List(PAGE_VISUALS_DEFAULT_STATE).tag(sync=True)

    _report_bookmark_name = Unicode(REPORT_BOOKMARK_DEFAULT_NAME).tag(sync=True)

    _report_bookmarks = List(REPORT_BOOKMARKS_DEFAULT_STATE).tag(sync=True)
    _get_bookmarks_request = Bool(GET_BOOKMARKS_REQUEST_DEFAULT_STATE).tag(sync=True)

    _token_expired = Bool(TOKEN_EXPIRED_DEFAULT_STATE).tag(sync=True)

    _client_error = Unicode(CLIENT_ERROR_DEFAULT_STATE).tag(sync=True)

    @validate('_export_visual_data_request')
    def _valid_export_visual_data_request(self, proposal):
        if proposal['value'] != self.EXPORT_VISUAL_DATA_REQUEST_DEFAULT_STATE:
            if (type(proposal['value']['pageName']) is not str):
                raise TraitError('Invalid pageName ', proposal['value']['pageName'])
            if (type(proposal['value']['visualName']) is not str):
                raise TraitError('Invalid visualName ', proposal['value']['visualName'])
            if (type(proposal['value']['rows']) is not int) or (proposal['value']['rows'] < 0):
                raise TraitError('Invalid rows ', proposal['value']['rows'])
            if type(proposal['value']['exportDataType']) is not int:
                raise TraitError('Invalid exportDataType ', proposal['value']['underlyingData'])

        return proposal['value']

    # Traits validators
    @validate('_report_filters_request')
    def _valid_report_filters_request(self, proposal):
        if proposal['value'] != self.REPORT_FILTER_REQUEST_DEFAULT_STATE:
            if (type(proposal['value']['filters']) is not list):
                raise TraitError('Invalid filters ', proposal['value']['filters'])

        return proposal['value']

    @validate('_embed_config')
    def _valid_embed_config(self, proposal):
        if proposal['value'] != self.EMBED_CONFIG_DEFAULT_STATE:
            if (type(proposal['value']['type']) is not str):
                raise TraitError('Invalid type ', proposal['value']['type'])
            if (type(proposal['value']['accessToken']) is not str):
                raise TraitError('Invalid accessToken ', proposal['value']['accessToken'])
            if (type(proposal['value']['embedUrl']) is not str):
                raise TraitError('Invalid embedUrl ', proposal['value']['embedUrl'])
            if (type(proposal['value']['tokenType']) is not int):
                raise TraitError('Invalid tokenType ', proposal['value']['tokenType'])
            if (type(proposal['value']['tokenExpiration']) is not int):
                raise TraitError('Invalid tokenExpiration ', proposal['value']['tokenExpiration'])
            if (type(proposal['value']['viewMode']) is not int):
                raise TraitError('Invalid viewMode ', proposal['value']['viewMode'])
            if (type(proposal['value']['permissions']) is not int):
                raise TraitError('Invalid permissions ', proposal['value']['permissions'])

        return proposal['value']

    # Methods
    def __init__(self, access_token=None, embed_url=None, token_type=TokenType.AAD.value, group_id=None, report_id=None, auth=None, embed_token_request_body=None , view_mode=EmbedMode.VIEW.value, permissions=Permissions.READ.value, client_id=None, tenant=None, scopes=None, dataset_id=None, **kwargs):
        """Create an instance of Power BI report

        Args:
            access_token (string): Optional.
                access token, which will be used to embed a Power BI report.
                If not provided, authentication object will be used (to be provided using `auth` parameter)

            embed_url (string): Optional.
                embed URL of Power BI report.
                If not provided, `group_id` and `report_id` parameters will be used to generate embed URL

            token_type (number): Optional.
                type of access token (0: AAD, 1: EMBED).
                (Default = AAD)

            group_id (string): Optional.
                Id of Power BI Group or Workspace where your report resides.
                It will be used if `embed_url` is not provided

            report_id (string): Optional.
                Id of Power BI report.
                It will be used if `embed_url` is not provided

            auth (object): Optional.
                Authentication object.
                It will be used if `access_token` is not provided.
                If not provided, Power BI User will be authenticated automatically using Device Flow authentication

            embed_token_request_body (JSON): Optional.
                JSON formatted request body to be used while calling Reports GenerateTokenInGroup API.
                \n For embedding Power BI report, refer: https://docs.microsoft.com/en-us/rest/api/power-bi/embedtoken/reports_generatetokeningroup.
                \n For creating Power BI report, refer: https://docs.microsoft.com/en-us/rest/api/power-bi/embedtoken/datasets_generatetokeningroup.
                It will be used if MasterUserAuthentication or ServicePrincipalAuthentication class object is provided using `auth` parameter.
                (Default = { "accessLevel": "View" })

            view_mode (number): Optional.
                Mode for embedding Power BI report (VIEW: 0, EDIT: 1, CREATE: 2).
                To be provided if you want to edit or create a report.
                (Default = VIEW)
            
            permissions (number): Optional.
                Permissions required while embedding report in EDIT mode.
                Values for permissions:
                \n `READ` - Users can view the report.
                \n `READWRITE` - Users can view, edit, and save the report.
                \n `COPY` - Users can save a copy of the report by using Save As.
                \n `CREATE` - Users can create a new report.
                \n `ALL` - Users can create, view, edit, save, and save a copy of the report.
                \n To be provided if the report is embedded in EDIT mode by passing `1` in `view_mode` parameter.
                (Default = READ)

            client_id (string): Optional.
                Your app has a client Id after you register it on AAD.
                To be provided if user wants to authenticate using own Azure AD app and `access_token` or `auth` is not provided.
                Power BI User will be authenticated automatically using Device Flow authentication using this client Id.
                (Default = Microsoft Azure Cross-platform Command Line Interface AAD app Id)

            scopes (list[string]): Optional.
                Scopes required to access Power BI API
                (Default = Power BI API default permissions)

            tenant (string): Optional.
                Organization tenant Id
                (Default = "organizations")

            dataset_id (string): Optional.
                Create report based on the dataset configured on Power BI workspace.
                To be provided if user wants to create a report.

        Returns:
            object: Report object
        """
        token_expiration = 0
        try:
            # Get access token for the report using authentication
            if not access_token:
                if not auth:
                    if not Report._auth:
                        if view_mode == EmbedMode.CREATE.value:
                            if not client_id:
                                raise Exception("client_id is required")

                            if not scopes:
                                scopes = CREATE_REPORT_SCOPES

                            # Set DeviceCodeLoginAuthentication as authentication method to get access token for creating Power BI report
                            Report._auth = DeviceCodeLoginAuthentication(client_id=client_id, scopes=scopes, tenant=tenant)
                        else:
                            # Set DeviceCodeLoginAuthentication to be the default global authentication method
                            Report._auth = DeviceCodeLoginAuthentication(client_id=client_id, scopes=scopes, tenant=tenant)
                    auth = Report._auth
                self._auth = auth

                # Perform UserOwnsData embedding
                if self._auth.embed_type is EmbedType.USEROWNSDATA.value:
                    access_token = self._auth.get_access_token()
                    token_type = TokenType.AAD.value
                    token_expiration = self._auth.get_access_token_details().get('id_token_claims').get('exp')

                # Perform AppOwnsData embedding
                else:
                    if not embed_token_request_body:
                        embed_token_request_body = self.DEFAULT_EMBED_TOKEN_REQUEST_BODY

                    # Generate embed token using access token
                    if view_mode == EmbedMode.CREATE.value:
                        if not group_id or not dataset_id:
                            raise Exception("Group Id and Dataset Id are required")
                        access_token = self._generate_embed_token(group_id=group_id, report_id=None, dataset_id=dataset_id, access_token=self._auth.get_access_token(), token_request_body=embed_token_request_body)
                    else:
                        if not group_id or not report_id:
                            raise Exception("Group Id and Report Id are required")
                        access_token = self._generate_embed_token(group_id=group_id, report_id=report_id, dataset_id=None, access_token=self._auth.get_access_token(), token_request_body=embed_token_request_body)
                    token_type = TokenType.EMBED.value

            # Get embed URL for the report using access token
            if not embed_url:
                token = access_token
                if token_type == TokenType.EMBED.value:
                    if not self._auth:
                        raise Exception("Cannot get embed URL using embed token")
                    token = self._auth.get_access_token()

                if view_mode == EmbedMode.CREATE.value:
                    if not group_id or not dataset_id:
                        raise Exception("Group Id and Dataset Id are required")
                    request_url = f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/datasets/{dataset_id}"
                    response = requests.get(request_url, headers={'Authorization': 'Bearer ' + token})
                    if not response.ok:
                        raise Exception("Get embed URL failed with status code ", response.status_code)
                    embed_url = response.json()['createReportEmbedURL']
                else:
                    if not group_id or not report_id:
                        raise Exception("Group Id and Report Id are required")
                    request_url = f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/reports/{report_id}"
                    response = requests.get(request_url, headers={'Authorization': 'Bearer ' + token})
                    if not response.ok:
                        raise Exception("Get embed URL failed with status code ", response.status_code)
                    embed_url = response.json()['embedUrl']
        except Exception as ex:
            raise Exception("Could not create access token or embed URL: ", ex)

        # Tells if Power BI events are being observed
        self._observing_events = False

        # Registered Power BI event handlers methods
        self._registered_event_handlers = dict(
            self.REGISTERED_EVENT_HANDLERS_DEFAULT_STATE)

        self._set_embed_config(access_token=access_token, embed_url=embed_url, view_mode=view_mode, permissions=permissions, dataset_id=dataset_id, token_type=token_type, token_expiration=token_expiration)
        self.observe(self._update_access_token, '_token_expired')

        # Init parent class DOMWidget
        super(Report, self).__init__(**kwargs)

    def _update_access_token(self, change):
        if change.new == True:
            if not self._auth:
                raise Exception("Authentication context not found")
            self._auth.refresh_token()
            self._set_embed_config(access_token=self._auth.get_access_token(), embed_url=self._embed_config['embedUrl'], view_mode=self._embed_config['viewMode'], permissions=self._embed_config['permissions'], dataset_id=self._embed_config['datasetId'], token_type=self._embed_config['tokenType'], token_expiration=self._auth.get_access_token_details().get('id_token_claims').get('exp'))
            self._token_expired = bool(self.TOKEN_EXPIRED_DEFAULT_STATE)

    def set_access_token(self, access_token):
        """Set access token for Power BI report

        Args:
            access_token (string): report access token
        """
        if not access_token:
            raise Exception("Access token cannot be empty")
        self._set_embed_config(access_token=access_token, embed_url=self._embed_config['embedUrl'], view_mode=self._embed_config['viewMode'], permissions=self._embed_config['permissions'], dataset_id=self._embed_config['datasetId'], token_type=self._embed_config['tokenType'], token_expiration=self._embed_config['tokenExpiration'])

    def _set_embed_config(self, access_token, embed_url, view_mode, permissions, dataset_id, token_type, token_expiration):
        """Set embed configuration parameters of Power BI report

        Args:
            access_token (string): report access token
            embed_url (string): report embed URL
            view_mode (number): mode for embedding Power BI report (0: View, 1: Edit, 2: Create)
            permissions (number): permissions required while embedding report in Edit mode
            dataset_id (string): create report based on the dataset configured on Power BI workspace
            token_type (number): type of access token (0: Aad, 1: Embed)
            token_expiration (number): expiration timestamp of the access token
        """
        self._embed_config = {
            'type': 'report',
            'accessToken': access_token,
            'embedUrl': embed_url,
            'tokenType': token_type,
            'tokenExpiration': token_expiration,
            'viewMode': view_mode,
            'permissions': permissions,
            'datasetId': dataset_id
        }
        self._embedded = False

    def set_dimensions(self, container_height, container_width):
        """Set width and height of Power BI report in px

        Args:
            container_height (number): report height
            container_width (number): report width
        """
        if not self._embedded:
            raise Exception(self.REPORT_NOT_EMBEDDED_MESSAGE)
        if container_height < 0:
            raise TraitError('Invalid report height ', container_height)
        if container_width < 0:
            raise TraitError('Invalid report width ', container_width)

        self.container_height = container_height
        self.container_width = container_width

    def export_visual_data(self, page_name, visual_name, rows=10, export_data_type=ExportDataType.SUMMARIZED.value):
        """Returns the data of given visual of the embedded Power BI report

        Args:
            page_name (string): Page name of the report's page containing the target visual
            visual_name (string): Visual's unique name 
            rows (int, optional): Number of rows of data. Defaults to 10
            export_data_type (number, optional): Type of data to be exported (SUMMARIZED: 0, UNDERLYING: 1).
                (Default = SUMMARIZED)

        Returns:
            string: visual's exported data
        """
        if not self._embedded:
            raise Exception(self.REPORT_NOT_EMBEDDED_MESSAGE)

        # Start exporting data on client side
        self._export_visual_data_request = {
            'pageName': page_name,
            'visualName': visual_name,
            'rows': rows,	
            'exportDataType': export_data_type
        }

        # Check if ipython kernel is available
        if get_ipython():
            # Wait for client-side to send visual data
            with ui_events() as ui_poll:
                # While visual data is not received
                while self._visual_data == self.VISUAL_DATA_DEFAULT_STATE:
                    ui_poll(self.PROCESS_EVENTS_ITERATION)
                    time.sleep(self.POLLING_INTERVAL)
                    if self._client_error:
                        break

        exported_data = self._visual_data

        # Reset the _export_visual_data_request and _visual_data's value
        self._export_visual_data_request = dict(self.EXPORT_VISUAL_DATA_REQUEST_DEFAULT_STATE)
        self._visual_data = self.VISUAL_DATA_DEFAULT_STATE

        # Throw client side error
        if self._client_error:
            error_message = self._client_error
            self._client_error = self.CLIENT_ERROR_DEFAULT_STATE
            raise Exception(error_message)

        return exported_data

    def on(self, event, callback):
        """Register a callback to execute when the report emits the target event
        Parameters

        Args:
            event (string): Name of Power BI event (eg. 'loaded', 'rendered', 'error')
            callback (function): User defined function. Callback function is invoked with event details as parameter
        """
        # Check if event is one of the Report.ALLOWED_EVENTS list
        if event not in self.ALLOWED_EVENTS:
            raise Exception(event + " event is not valid")

        # Check if event is one of the Report.SUPPORTED_EVENTS list
        if event not in self.SUPPORTED_EVENTS:
            raise Exception(event + " event is not supported")

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

        # Check if already observing events
        if not self._observing_events:

            # Prevents calling DOMWidget.observe() again
            self._observing_events = True

            # Start observing Power BI events
            self.observe(get_event_data, '_event_data')

    def off(self, event):
        """Unregisters a callback on target event
        Parameters

        Args:
            event (string): Name of Power BI event (eg. 'loaded', 'rendered', 'error')
        """
        # Check if event is one of the Report.ALLOWED_EVENTS list
        if event not in self.ALLOWED_EVENTS:
            raise Exception(event + " event is not valid")

        # Check if event is one of the Report.SUPPORTED_EVENTS list
        if event not in self.SUPPORTED_EVENTS:
            raise Exception(event + " event is not supported")

        # Remove handler if registered for the current event
        if event in self._registered_event_handlers:
            self._registered_event_handlers.pop(event)

    def get_filters(self):
        """Returns the list of filters applied on the embedded Power BI report

        Returns:
            list: list of filters
        """
        if not self._embedded:
            raise Exception(self.REPORT_NOT_EMBEDDED_MESSAGE)

        # Start getting filters on client side
        self._get_filters_request = True

        # Check if ipython kernel is available
        if get_ipython():
            # Wait for client-side to send list of filters
            with ui_events() as ui_poll:
                # While list of report filters is not received
                while self._report_filters == self.REPORT_FILTERS_DEFAULT_STATE:
                    ui_poll(self.PROCESS_EVENTS_ITERATION)
                    time.sleep(self.POLLING_INTERVAL)
                    if self._client_error:
                        break

        filters = self._report_filters

        # Reset the _get_filters_request and _report_filters's value
        self._get_filters_request = bool(self.GET_FILTERS_REQUEST_DEFAULT_STATE)
        self._report_filters = list(self.REPORT_FILTERS_DEFAULT_STATE)

        # Throw client side error
        if self._client_error:
            error_message = self._client_error
            self._client_error = self.CLIENT_ERROR_DEFAULT_STATE
            raise Exception(error_message)

        return filters

    def update_filters(self, filters):
        """Set report level filters in the embedded report.
            Currently supports models.FiltersOperations.Add

        Args:
            filters ([models.ReportLevelFilters]): List of report level filters

        Raises:
            Exception: When report is not embedded
        """
        if not self._embedded:
            raise Exception(self.REPORT_NOT_EMBEDDED_MESSAGE)

        self._report_filters_request = {
            'filters': filters,
            'request_completed': False
        }

        # Check if ipython kernel is available
        if get_ipython():
            # Wait for client-side to update filters
            with ui_events() as ui_poll:
                # While filters are not applied
                while self._report_filters_request != self.REPORT_FILTER_REQUEST_DEFAULT_STATE:
                    ui_poll(self.PROCESS_EVENTS_ITERATION)
                    time.sleep(self.POLLING_INTERVAL)
                    if self._client_error:
                        break

        # Reset the _report_filters_request's value
        self._report_filters_request = dict(self.REPORT_FILTER_REQUEST_DEFAULT_STATE)

        # Throw client side error
        if self._client_error:
            error_message = self._client_error
            self._client_error = self.CLIENT_ERROR_DEFAULT_STATE
            raise Exception(error_message)

    def remove_filters(self):
        """Remove all report level filters from the embedded report

        Raises:
            Exception: When report is not embedded
        """
        self.update_filters([])

    def get_pages(self):
        """Returns the list of pages of the embedded Power BI report

        Returns:
            list: list of pages
        """
        if not self._embedded:
            raise Exception(self.REPORT_NOT_EMBEDDED_MESSAGE)

        # Start getting pages on client side
        self._get_pages_request = True

        # Check if ipython kernel is available
        if get_ipython():
            # Wait for client-side to send list of pages
            with ui_events() as ui_poll:
                # While list of report pages is not received
                while self._report_pages == self.REPORT_PAGES_DEFAULT_STATE:
                    ui_poll(self.PROCESS_EVENTS_ITERATION)
                    time.sleep(self.POLLING_INTERVAL)
                    if self._client_error:
                        break

        pages = self._report_pages

        # Reset the get_pages_request and report_pages's value
        self._get_pages_request = bool(self.GET_PAGES_REQUEST_DEFAULT_STATE)
        self._report_pages = list(self.REPORT_PAGES_DEFAULT_STATE)

        # Throw client side error
        if self._client_error:
            error_message = self._client_error
            self._client_error = self.CLIENT_ERROR_DEFAULT_STATE
            raise Exception(error_message)

        return pages

    def visuals_on_page(self, page_name):
        """Returns the list of visuals of the given page of the embedded Power BI report

        Args:
            page_name (string): Page name of the embedded report

        Returns:
            list: list of visuals
        """
        if not self._embedded:
            raise Exception(self.REPORT_NOT_EMBEDDED_MESSAGE)

        # Start getting visuals on client side
        self._get_visuals_page_name = page_name

        # Check if ipython kernel is available
        if get_ipython():
            # Wait for client-side to send list of visuals
            with ui_events() as ui_poll:
                # While list of visuals is not received
                while self._page_visuals == self.PAGE_VISUALS_DEFAULT_STATE:
                    ui_poll(self.PROCESS_EVENTS_ITERATION)
                    time.sleep(self.POLLING_INTERVAL)
                    if self._client_error:
                        break

        visuals = self._page_visuals

        # Reset the get_visuals_page_name and page_visuals's value
        self._get_visuals_page_name = self.GET_VISUALS_DEFAULT_PAGE_NAME
        self._page_visuals = list(self.PAGE_VISUALS_DEFAULT_STATE)

        # Throw client side error
        if self._client_error:
            error_message = self._client_error
            self._client_error = self.CLIENT_ERROR_DEFAULT_STATE
            raise Exception(error_message)

        return visuals

    def set_bookmark(self, bookmark_name):
        """Applies a bookmark by name on the embedded report.

        Args:
            bookmark_name (string) : Bookmark Name
        Raises:
            Exception: When report is not embedded
        """

        if not self._embedded:
            raise Exception(self.REPORT_NOT_EMBEDDED_MESSAGE)

        self._report_bookmark_name = bookmark_name

    def get_bookmarks(self):
        """Returns the list of bookmarks of the embedded Power BI report

        Returns:
            list: list of bookmarks

        Raises:
            Exception: When report is not embedded
        """

        if not self._embedded:
            raise Exception(self.REPORT_NOT_EMBEDDED_MESSAGE)

        # Start getting bookmarks on client side
        self._get_bookmarks_request = True

        # Check if ipython kernel is available
        if get_ipython():
            # Wait for client-side to send list of bookmarks
            with ui_events() as ui_poll:
                # While list of report bookmark(s) is not received
                while self._report_bookmarks == self.REPORT_BOOKMARKS_DEFAULT_STATE:
                    ui_poll(self.PROCESS_EVENTS_ITERATION)
                    time.sleep(self.POLLING_INTERVAL)
                    if self._client_error:
                        break

        bookmarks = self._report_bookmarks

        if bookmarks == ['']:
            bookmarks = self.REPORT_BOOKMARKS_DEFAULT_STATE

        # Reset the _get_bookmarks_request and _report_bookmarks values
        self._get_bookmarks_request = bool(self.GET_BOOKMARKS_REQUEST_DEFAULT_STATE)
        self._report_bookmarks = list(self.REPORT_BOOKMARKS_DEFAULT_STATE)

        # Throw client side error
        if self._client_error:
            error_message = self._client_error
            self._client_error = self.CLIENT_ERROR_DEFAULT_STATE
            raise Exception(error_message)

        return bookmarks

    # Utility method to generate embed token for a Power BI report
    def _generate_embed_token(self, group_id, report_id, dataset_id, access_token, token_request_body):
        """Generate embed token for Power BI report
            Refer: https://docs.microsoft.com/en-us/rest/api/power-bi/embedtoken/reports_generatetokeningroup

        Args:
            group_id (string): Id of Power BI Group or Workspace where your report resides.
            report_id (string): Id of Power BI report.
            access_token (string): access token, which will be used to generate embed token for Power BI report.
            token_request_body (string): JSON formatted request body to be used while calling Reports GenerateTokenInGroup API.

        Returns:
            string: Report embed token
        """
        if dataset_id:
            request_url = f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/datasets/{dataset_id}/GenerateToken"
        else:
            request_url = f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/reports/{report_id}/GenerateToken"
        response = requests.post(request_url, headers={'Authorization': 'Bearer ' + access_token}, data=token_request_body)
        if not response.ok:
            raise Exception("Generate embed token failed with status code ", response.status_code)

        return response.json()['token']
