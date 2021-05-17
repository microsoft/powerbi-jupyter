#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

"""
Authenticates a Power BI User and acquires an access token
"""

import json
import msal

from .models import EmbedType

# Acquire access token by concatenating tenant with Authority URI
AUTHORITY_URI = "https://login.microsoftonline.com/"

# NOTE: The client id used below is for "Microsoft Azure Cross-platform Command Line Interface" AAD app and a well known that already exists for all Azure services.
#       Refer blog: https://docs.microsoft.com/en-us/samples/azure-samples/data-lake-analytics-python-auth-options/authenticating-your-python-application-against-azure-active-directory/
DEFAULT_CLIENT_ID = "04b07795-8ddb-461a-bbee-02f9e1bf7b46"

# Using Power BI default permissions
DEFAULT_SCOPES = ["https://analysis.windows.net/powerbi/api/.default"]

# Power BI permissions for creating report
CREATE_REPORT_SCOPES = ["https://analysis.windows.net/powerbi/api/Dataset.ReadWrite.All", "https://analysis.windows.net/powerbi/api/Content.Create", "https://analysis.windows.net/powerbi/api/Workspace.ReadWrite.All"]

class AuthenticationResult:

    # Methods
    def __init__(self, client_id, scopes, authority_uri, access_token_result):
        """Create an instance of Authentication

        Args:
            client_id (string): Your app has a client Id after you register it on AAD
            scopes (list[string]): Scopes required to access Power BI API
            authority_uri (string): Microsoft authority URI used for authentication
            access_token_result (dict): Authentication result

        Returns:
            object: Authentication object
        """
        self._access_token_result = access_token_result
        self._client_id = client_id
        self._scopes = scopes
        self.authority_uri = authority_uri

    def get_access_token(self):
        """Returns the access token

        Returns:
            string: access token
        """

        return self._access_token_result.get('access_token')

    def get_access_token_details(self):
        """Returns the authentication result with access token

        Returns:
            dict: authentication result
        """

        return self._access_token_result

    def refresh_token(self):
        """Acquire token(s) based on a refresh token obtained from authentication result
        """
        app = msal.PublicClientApplication(client_id=self._client_id, authority=self.authority_uri)
        token_result = app.acquire_token_by_refresh_token(self._access_token_result.get('refresh_token'), self._scopes)
        if "access_token" not in token_result:
            raise RuntimeError(token_result.get('error_description'))
        self._access_token_result = token_result


class DeviceCodeLoginAuthentication(AuthenticationResult):

    # Methods
    def __init__(self, client_id=None, scopes=None, tenant=None):
        """Initiate a Device Flow Auth instance

        Args:
            client_id (string): Optional.
                Your app has a client Id after you register it on AAD.
                (Default = Microsoft Azure Cross-platform Command Line Interface AAD app Id)
            scopes (list[string]): Optional.
                Scopes required to access Power BI API
                (Default = Power BI API default permissions)
            tenant (string): Optional.
                Organization tenant Id
                (Default = "organizations")

        Returns:
            object: Device Flow object
        """
        # To perform User Owns Data embedding
        self.embed_type = EmbedType.USEROWNSDATA.value

        if not tenant:
            tenant = 'organizations'
        self.authority_uri = AUTHORITY_URI + tenant

        if not client_id:
            client_id = DEFAULT_CLIENT_ID
        self.client_id = client_id

        if not scopes:
            scopes = DEFAULT_SCOPES
        self.scopes = scopes
        auth_result = self._acquire_token_device_code()
        super().__init__(client_id, scopes, self.authority_uri, auth_result)

    def _acquire_token_device_code(self):
        """Returns the authentication result captured using device flow

        Returns:
            dict: authentication result
        """
        app = msal.PublicClientApplication(client_id=self.client_id, authority=self.authority_uri)
        flow = app.initiate_device_flow(self.scopes)

        if "user_code" not in flow:
            raise ValueError("Fail to create device flow. Err: %s" % json.dumps(flow, indent=4))

        # Display the device code
        print("Performing interactive authentication. Please follow the instructions on the terminal.\n", flow["message"])

        # Ideally you should wait here, in order to save some unnecessary polling
        result = app.acquire_token_by_device_flow(flow)
        # By default it will block
        # You can follow this instruction to shorten the block time
        #    https://msal-python.readthedocs.io/en/latest/#msal.PublicClientApplication.acquire_token_by_device_flow
        # or you may even turn off the blocking behavior,
        # and then keep calling acquire_token_by_device_flow(flow) in your own customized loop.

        if "access_token" in result:
            print("You have logged in.\nInteractive authentication successfully completed.")
            return result
        else:
            raise RuntimeError(result.get("error_description"))


class InteractiveLoginAuthentication(AuthenticationResult):

    # Methods
    def __init__(self, client_id=None, scopes=None, tenant=None):
        """Acquire token interactively i.e. via a local browser

        Args:
            client_id (string): Optional.
                Your app has a client Id after you register it on AAD.
                (Default = Microsoft Azure Cross-platform Command Line Interface AAD app Id)
            scopes (list[string]): Optional.
                Scopes required to access Power BI API
                (Default = Power BI API default permissions)
            tenant (string): Optional.
                Organization tenant Id
                (Default = "organizations")

        Returns:
            object: Interactive authentication object
        """
        # To perform User Owns Data embedding
        self.embed_type = EmbedType.USEROWNSDATA.value

        if not tenant:
            tenant = 'organizations'
        self.authority_uri = AUTHORITY_URI + tenant

        if not client_id:
            client_id = DEFAULT_CLIENT_ID
        self.client_id = client_id

        if not scopes:
            scopes = DEFAULT_SCOPES
        self.scopes = scopes
        auth_result = self._acquire_token_interactive()
        super().__init__(client_id, scopes, self.authority_uri, auth_result)

    def _acquire_token_interactive(self):
        """Returns the authentication result captured using interactive login

        Returns:
            dict: authentication result
        """
        app = msal.PublicClientApplication(client_id=self.client_id, authority=self.authority_uri)
        print("A local browser window will be open for interactive sign in.")
        result = app.acquire_token_interactive(self.scopes)

        if "access_token" in result:
            print("You have logged in.\nInteractive authentication successfully completed.")
            return result
        else:
            raise RuntimeError(result.get("error_description"))

class MasterUserAuthentication(AuthenticationResult):

    # Methods
    def __init__(self, username, password, client_id=None, scopes=None, tenant=None):
        """Acquire token with username and password

        Args:
            username (string): UPN in the form of an email address.
            password (string): Password to authenticate Power BI user
            client_id (string): Optional.
                Your app has a client Id after you register it on AAD.
                (Default = Microsoft Azure Cross-platform Command Line Interface AAD app Id)
            scopes (list[string]): Optional.
                Scopes required to access Power BI API
                (Default = Power BI API default permissions)
            tenant (string): Optional.
                Organization tenant Id
                (Default = "organizations")

        Returns:
            object: Master User authentication object
        """
        # To perform App Owns Data embedding
        self.embed_type = EmbedType.APPOWNSDATA.value

        if not tenant:
            tenant = 'organizations'
        self.authority_uri = AUTHORITY_URI + tenant

        if not client_id:
            client_id = DEFAULT_CLIENT_ID
        self.client_id = client_id

        if not scopes:
            scopes = DEFAULT_SCOPES
        self.scopes = scopes

        self.username = username
        self.password = password
        auth_result = self._acquire_token_with_master_user()
        super().__init__(client_id, scopes, self.authority_uri, auth_result)

    def _acquire_token_with_master_user(self):
        """Returns the authentication result captured using Master User authentication

        Returns:
            dict: authentication result
        """
        app = msal.PublicClientApplication(client_id=self.client_id, authority=self.authority_uri)
        print("Authenticating master user.")
        result = app.acquire_token_by_username_password(username=self.username, password=self.password, scopes=self.scopes)

        if "access_token" in result:
            print("Master user authentication successfully completed.")
            return result
        else:
            raise RuntimeError(result.get("error_description"))


class ServicePrincipalAuthentication(AuthenticationResult):

    # Methods
    def __init__(self, client_id, client_secret, tenant, scopes=None):
        """Acquire token with Service Principal

        Args:
            client_id (string): Your app has a client Id after you register it on AAD
            client_secret (string): Client secret associated with the AAD app
            tenant (string): Organization tenant Id
            scopes (list[string]): Optional.
                Scopes required to access Power BI API
                (Default = Power BI API default permissions)

        Returns:
            object: Service Principal authentication object
        """
        # To perform App Owns Data embedding
        self.embed_type = EmbedType.APPOWNSDATA.value

        if not scopes:
            scopes = DEFAULT_SCOPES
        self.scopes = scopes

        self.authority_uri = AUTHORITY_URI + tenant
        self.client_secret = client_secret
        self.client_id = client_id
        auth_result = self._acquire_token_with_service_principal()
        super().__init__(client_id, scopes, self.authority_uri, auth_result)

    def _acquire_token_with_service_principal(self):
        """Returns the authentication result captured using Service Principal authentication

        Returns:
            dict: authentication result
        """
        app = msal.ConfidentialClientApplication(client_id=self.client_id, client_credential=self.client_secret, authority=self.authority_uri)
        print("Authenticating service principal.")
        result = app.acquire_token_for_client(self.scopes)

        if "access_token" in result:
            print("Service principal authentication successfully completed.")
            return result
        else:
            raise RuntimeError(result.get("error_description"))

    def refresh_token(self):
        """Acquire token(s) with Service Principal.
            Override parent class refresh_token method.
        """
        self._access_token_result = self._acquire_token_with_service_principal()
