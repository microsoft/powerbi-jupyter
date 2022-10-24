#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

from ..authentication import AuthenticationResult
from ..report import Report
from ..utils import get_access_token_details

ACCESS_TOKEN = 'dummy_access_token'
TOKEN_EXPIRATION = 30
AUTH = AuthenticationResult({ 'access_token': ACCESS_TOKEN, 'id_token_claims': { 'exp': TOKEN_EXPIRATION } })

class TestGetAccessTokenDetails:
    def test_happy_path_access_token(self):
        access_token, token_expiration = get_access_token_details(powerbi_widget=Report, auth=ACCESS_TOKEN)
        assert access_token == ACCESS_TOKEN
        assert token_expiration == 0
    
    def test_happy_path_auth_result(self):
        access_token, token_expiration = get_access_token_details(powerbi_widget=Report, auth=AUTH)
        assert access_token == ACCESS_TOKEN
        assert token_expiration == TOKEN_EXPIRATION

    def test_invalid_auth(self):
        invalid_auth = 1234
        try:
            get_access_token_details(powerbi_widget=Report, auth=invalid_auth)
        except Exception as ex:
            assert True
            return
        
        # should not get here
        assert False