#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

"""
Authenticates a Power BI User and acquires an access token
"""

import json
import msal

# NOTE: The client id used below is for "Power BI Client Integrations" first party application
CLIENT_ID = "1aea3f97-edc6-4453-a59b-b88b0b803711"

# Authority template string is used with tenant_id if defined within authentication
AUTHORITY_STR = "https://login.microsoftonline.com/"

# Using Power BI default permissions
DEFAULT_SCOPES = ["https://analysis.windows.net/powerbi/api/.default"]

# Global level authentication
AUTH = None

class AuthenticationResult:

    # Methods
    def __init__(self):
        """ Create an instance of AuthenticationResult

        Returns:
            object: AuthenticationResult object. The authentication result object should be passed only to trusted code in your notebook.
        """
        self._app = None

    def get_access_token(self, force_refresh=False):
        """ Returns the access token

        Returns:
            string: access token
        """
        if self._app is None:
            raise RuntimeError('No application found')

        accounts = self._app.get_accounts()
        if len(accounts) == 0:
            raise RuntimeError('No accounts found for application')

        token_result = self._app.acquire_token_silent_with_error(
            scopes=DEFAULT_SCOPES, account=accounts[0], force_refresh=force_refresh)

        if not token_result:
            raise RuntimeError('Failed to get access token')

        if ('access_token' not in token_result) or ('error' in token_result):
            raise RuntimeError(token_result.get(
                'error', 'Failed to get access token'))

        return token_result.get('access_token')


class DeviceCodeLoginAuthentication(AuthenticationResult):

    # Methods
    def __init__(self, tenant_id=None):
        """ Initiate a Device Flow Auth instance

        Args:
            tenant_id (string): Optional.
                Id of Power BI tenant where your report resides.

        Returns:
            object: Device flow object. The device flow object should be passed only to trusted code in your notebook.
        """
        super().__init__()
        CheckGlobalAuth()
        self._acquire_token_device_code(tenant_id)

    def _acquire_token_device_code(self, tenant_id=None):
        """ Acquires a token with device code flow and saves the public client application
        """
        if not tenant_id:
            app = msal.PublicClientApplication(client_id=CLIENT_ID)
        else:
            app = msal.PublicClientApplication(client_id=CLIENT_ID, authority='{0}{1}'.format(AUTHORITY_STR, tenant_id))
        flow = app.initiate_device_flow(scopes=DEFAULT_SCOPES)

        if "user_code" not in flow:
            raise ValueError("Fail to create device flow. Err: %s" %
                             json.dumps(flow, indent=4))

        # Display the device code
        print("Performing device flow authentication. Please follow the instructions below.\n{0}".format(
            flow["message"]))

        # Ideally you should wait here, in order to save some unnecessary polling
        result = app.acquire_token_by_device_flow(flow)
        # By default it will block
        # You can follow this instruction to shorten the block time
        #    https://msal-python.readthedocs.io/en/latest/#msal.PublicClientApplication.acquire_token_by_device_flow
        # or you may even turn off the blocking behavior,
        # and then keep calling acquire_token_by_device_flow(flow) in your own customized loop.

        if "access_token" in result:
            print("\nDevice flow authentication successfully completed.\nYou are now logged in .\n\nThe result should be passed only to trusted code in your notebook.")
            self._app = app
        else:
            error_message = f"Authentication failed. Try again.\nDetails: {result.get('error_description')}"
            raise RuntimeError(error_message)


class InteractiveLoginAuthentication(AuthenticationResult):

    # Methods
    def __init__(self, tenant_id=None):
        """Acquire token interactively i.e. via a local browser

        Args:
            tenant_id (string): Optional.
                Id of Power BI tenant where your report resides.

        Returns:
            object: Interactive authentication object. The interactive authentication object should be passed only to trusted code in your notebook.
        """
        super().__init__()
        CheckGlobalAuth()
        self._acquire_token_interactive(tenant_id)

    def _acquire_token_interactive(self, tenant_id=None):
        """ Acquires a token interactively i.e. via a local browser and saves the public client application
        """
        if not tenant_id:
            app = msal.PublicClientApplication(client_id=CLIENT_ID)
        else:
            app = msal.PublicClientApplication(client_id=CLIENT_ID, authority=AUTHORITY_STR+tenant_id)
        print("A local browser window will open for interactive sign in.")
        result = app.acquire_token_interactive(scopes=DEFAULT_SCOPES)

        if "access_token" in result:
            print("\nInteractive authentication successfully completed.\nYou are now logged in.\n\nThe result should be passed only to trusted code in your notebook.")
            self._app = app
        else:
            error_message = f"Authentication failed. Try again.\nDetails: {result.get('error_description')}"
            raise RuntimeError(error_message)
        
def CheckGlobalAuth():
    if AUTH is not None:
        raise Exception("Current scenario does not require manual authentication, proceed to create your Power BI items without passing the 'auth' object.")
