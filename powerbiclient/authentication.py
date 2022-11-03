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
    def __init__(self, access_token_result):
        """ Create an instance of AuthenticationResult

        Args:
            access_token_result (dict): Authentication result

        Returns:
            object: AuthenticationResult object
        """
        self._access_token_result = access_token_result

    def get_access_token(self):
        """ Returns the access token

        Returns:
            string: access token
        """

        return self._access_token_result.get('access_token')

    def get_access_token_details(self):
        """ Returns the authentication result with access token

        Returns:
            dict: authentication result
        """

        return self._access_token_result

    def refresh_token(self):
        """ Acquire token(s) based on a refresh token obtained from authentication result
        """
        app = msal.PublicClientApplication(client_id=CLIENT_ID)
        token_result = app.acquire_token_by_refresh_token(self._access_token_result.get('refresh_token'), DEFAULT_SCOPES)
        if "access_token" not in token_result:
            raise RuntimeError(token_result.get('error_description'))
        self._access_token_result = token_result


class DeviceCodeLoginAuthentication(AuthenticationResult):

    # Methods
    def __init__(self):
        """ Initiate a Device Flow Auth instance

        Returns:
            object: Device Flow object
        """
        auth_result = self._acquire_token_device_code()
        super().__init__(auth_result)

    def _acquire_token_device_code(self):
        """ Returns the authentication result captured using device flow

        Returns:
            dict: authentication result
        """
        app = msal.PublicClientApplication(client_id=CLIENT_ID)
        flow = app.initiate_device_flow(scopes=DEFAULT_SCOPES)

        if "user_code" not in flow:
            raise ValueError("Fail to create device flow. Err: %s" % json.dumps(flow, indent=4))

        # Display the device code
        print("Performing device flow authentication. Please follow the instructions below.\n{0}".format(flow["message"]))

        # Ideally you should wait here, in order to save some unnecessary polling
        result = app.acquire_token_by_device_flow(flow)
        # By default it will block
        # You can follow this instruction to shorten the block time
        #    https://msal-python.readthedocs.io/en/latest/#msal.PublicClientApplication.acquire_token_by_device_flow
        # or you may even turn off the blocking behavior,
        # and then keep calling acquire_token_by_device_flow(flow) in your own customized loop.

        if "access_token" in result:
            print("\nDevice flow authentication successfully completed.\nYou are now logged in.")
            return result
        else:
            raise RuntimeError(result.get("error_description"))


class InteractiveLoginAuthentication(AuthenticationResult):

    # Methods
    def __init__(self):
        """Acquire token interactively i.e. via a local browser

        Returns:
            object: Interactive authentication object
        """
        auth_result = self._acquire_token_interactive()
        super().__init__(auth_result)

    def _acquire_token_interactive(self):
        """Returns the authentication result captured using interactive login

        Returns:
            dict: authentication result
        """
        app = msal.PublicClientApplication(client_id=CLIENT_ID)
        print("A local browser window will open for interactive sign in.")
        result = app.acquire_token_interactive(scopes=DEFAULT_SCOPES)

        if "access_token" in result:
            print("\nInteractive authentication successfully completed.\nYou are now logged in.")
            return result
        else:
            raise RuntimeError(result.get("error_description"))