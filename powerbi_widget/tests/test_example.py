#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Microsoft.
# Distributed under the terms of the Modified BSD License.

import pytest

from ..report import Report

def test_example_creation_blank():
    access_token = ''
    embed_url = ''
    w = Report(access_token, embed_url)
    w.set_dimensions(0, 0)
