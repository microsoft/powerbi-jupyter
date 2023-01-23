#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

"""
Authenticates a Power BI User and acquires an access token
"""

import json
import msal

# NOTE: The client id used below is for "Power BI Powershell" first party application
CLIENT_ID = "23d8f6bd-1eb0-4cc2-a08c-7bf525c67bcd"

# Using Power BI default permissions
DEFAULT_SCOPES = ["https://analysis.windows.net/powerbi/api/.default"]


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
    def __init__(self):
        """ Initiate a Device Flow Auth instance

        Returns:
            object: Device flow object. The device flow object should be passed only to trusted code in your notebook.
        """
        super().__init__()
        self._acquire_token_device_code()

    def _acquire_token_device_code(self):
        """ Acquires a token with device code flow and saves the public client application
        """
        app = msal.PublicClientApplication(client_id=CLIENT_ID)
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
    def __init__(self):
        """Acquire token interactively i.e. via a local browser

        Returns:
            object: Interactive authentication object. The interactive authentication object should be passed only to trusted code in your notebook.
        """
        super().__init__()
        self._acquire_token_interactive()

    def _acquire_token_interactive(self):
        """ Acquires a token interactively i.e. via a local browser and saves the public client application
        """
        app = msal.PublicClientApplication(client_id=CLIENT_ID)
        print("A local browser window will open for interactive sign in.")
        result = app.acquire_token_interactive(scopes=DEFAULT_SCOPES)

        if "access_token" in result:
            print("\nInteractive authentication successfully completed.\nYou are now logged in.\n\nThe result should be passed only to trusted code in your notebook.")
            self._app = app
        else:
            error_message = f"Authentication failed. Try again.\nDetails: {result.get('error_description')}"
            raise RuntimeError(error_message)
