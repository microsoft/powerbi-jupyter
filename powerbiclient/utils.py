#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

from .authentication import DeviceCodeLoginAuthentication, AuthenticationResult

MODULE_NAME = "powerbi-jupyter-client"

#TODO: update method to convert df into dataset_config
def get_dataset_config(df, locale='en-US'):
    return {
        'locale': locale,
        'tableSchemaList': [
            {
            'name': "Table",
            'columns': [
                {
                    'name': "Name",
                    'dataType': "Text"
                },
                {
                    'name': "Id",
                    'dataType': "Int32"
                },
                {
                    'name': "Phone number",
                    'dataType': "Text"
                }
            ]
            }
        ],
        'data': [
            {
            'name': "Table",
            'rows': [["test1", "1", "123-456"], ["test2", "2", "456-789"]]
            }
        ]
    }

def is_dataset_create_config_valid(dataset_create_config):
    if dataset_create_config is None or type(dataset_create_config) is not dict:
        return False

    #TODO: add validation
    
    return True

def get_access_token_details(powerbi_widget, auth=None):
    """ Get access token details: access token and token expiration

    Args:
        powerbi_widget (Report | QuickVisulize): Required.
            One of Power BI widget classes, can be Report or QuickVisualize
        auth (string or object): Optional.
            We have 3 authentication options to embed a Power BI report:
                - Access token (string)
                - Authentication object (object) - instance of AuthenticationResult (DeviceCodeLoginAuthentication or InteractiveLoginAuthentication)
                - If not provided, Power BI user will be authenticated using Device Flow authentication

    Returns:
        tuple: (access_token, token_expiration)
    """

    # auth is the access token string
    if isinstance(auth, str):
        # In this authentication way we cannot refresh the access token so token_expiration should be None
        token_expiration = None
        return auth, token_expiration
    
    try:
        if auth is None:
            # Use DeviceCodeLoginAuthentication if no authentication is provided
            if not powerbi_widget._auth:
                powerbi_widget._auth = DeviceCodeLoginAuthentication()
            auth = powerbi_widget._auth
        elif not isinstance(auth, AuthenticationResult):
            raise Exception("Given auth parameter is invalid")
        else:
            powerbi_widget._auth = auth

        access_token = auth.get_access_token()
        token_expiration = auth.get_access_token_details().get('id_token_claims').get('exp')
        return access_token, token_expiration
    
    except Exception as ex:
        raise Exception("Could not get access token: {0}".format(ex))
