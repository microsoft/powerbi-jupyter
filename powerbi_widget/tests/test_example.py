#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Microsoft.
# Distributed under the terms of the Modified BSD License.

import pytest

from ..report import Report

def test_report_constructor():
    access_token = 'dummy_access_token'
    embed_url = 'dummy_embed_url'
    report = Report(access_token, embed_url)
    report.set_dimensions(0, 0)

    assert report.embed_config == {
        'type': 'report',
        'accessToken': access_token,
        'embedUrl': embed_url,
        'tokenType': 0
    }
