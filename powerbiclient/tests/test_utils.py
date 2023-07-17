#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

from pytest import raises
import pandas as pd
from unittest.mock import MagicMock
import pytest

from ..authentication import AuthenticationResult
from ..report import Report
from ..utils import get_access_token_details, get_dataset_config, is_dataset_create_config_valid

ACCESS_TOKEN = 'dummy_access_token'
LOCALE = 'dummy_locale'
TABLE_SCHEMA_COLUMNS = [{'name': 'col1', 'dataType': 'Number'}]
TABLE_SCHEMA_LIST = [
    {'name': 'dummy_table_name', 'columns': TABLE_SCHEMA_COLUMNS}]
DATA_ROWS = [[1]]
DATA = [{'name': 'dummy_table_name', 'rows': DATA_ROWS}]


class TestGetAccessTokenDetails:
    def test_happy_path_access_token(self):
        access_token = get_access_token_details(
            powerbi_widget=Report, auth=ACCESS_TOKEN)
        assert access_token == ACCESS_TOKEN

    def test_happy_path_auth_result(self):
        mock_auth = AuthenticationResult()
        mock_auth.get_access_token = MagicMock(return_value=ACCESS_TOKEN)
        access_token = get_access_token_details(
            powerbi_widget=Report, auth=mock_auth)
        assert access_token == ACCESS_TOKEN

    def test_invalid_auth(self):
        invalid_auth = 1234

        # Act + Assert
        with raises(Exception):
            get_access_token_details(powerbi_widget=Report, auth=invalid_auth)

class TestIsDatasetCreateConfigValid:
    def test_happy_path(self):
        assert is_dataset_create_config_valid(
            {'locale': LOCALE, 'tableSchemaList': TABLE_SCHEMA_LIST, 'data': DATA})

    def test_invalid_config(self):
        # dataset_create_config is None
        assert not is_dataset_create_config_valid(None)

        # dataset_create_config is not dict
        assert not is_dataset_create_config_valid('invalid_config')

        # dataset_create_config has wrong keys number
        assert not is_dataset_create_config_valid({'key1': 1})

    def test_invalid_locale(self):
        # locale key does not exist
        assert not is_dataset_create_config_valid(
            {'local': LOCALE, 'tableSchemaList': TABLE_SCHEMA_LIST, 'data': DATA})

        # locale is not a string
        assert not is_dataset_create_config_valid(
            {'locale': 1, 'tableSchemaList': TABLE_SCHEMA_LIST, 'data': DATA})

    def test_invalid_table_schema_list(self):
        # tableSchemaList key does not exist
        assert not is_dataset_create_config_valid(
            {'locale': LOCALE, 'tableSchem': TABLE_SCHEMA_LIST, 'data': DATA})

        # tableSchemaList is not a list
        assert not is_dataset_create_config_valid(
            {'locale': LOCALE, 'tableSchemaList': 1, 'data': DATA})

        # tableSchemaList is empty list
        assert not is_dataset_create_config_valid(
            {'locale': LOCALE, 'tableSchemaList': [], 'data': DATA})

        # table does not have name
        assert not is_dataset_create_config_valid({'locale': LOCALE, 'tableSchemaList': [
                                                  {'columns': TABLE_SCHEMA_COLUMNS}], 'data': DATA})

        # table does not have columns
        assert not is_dataset_create_config_valid({'locale': LOCALE, 'tableSchemaList': [
                                                  {'name': 'dummy_table_name'}], 'data': DATA})

    def test_invalid_data(self):
        # data key does not exist
        assert not is_dataset_create_config_valid(
            {'locale': LOCALE, 'tableSchem': TABLE_SCHEMA_LIST, 'dta': DATA})

        # data is not a list
        assert not is_dataset_create_config_valid(
            {'locale': LOCALE, 'tableSchemaList': TABLE_SCHEMA_LIST, 'data': 1})

        # data is empty list
        assert not is_dataset_create_config_valid(
            {'locale': LOCALE, 'tableSchemaList': TABLE_SCHEMA_LIST, 'data': []})

        # table does not have name
        assert not is_dataset_create_config_valid(
            {'locale': LOCALE, 'tableSchemaList': TABLE_SCHEMA_LIST, 'data': [{'rows': DATA_ROWS}]})

        # table does not have rows
        assert not is_dataset_create_config_valid(
            {'locale': LOCALE, 'tableSchemaList': TABLE_SCHEMA_LIST, 'data': [{'name': 'dummy_table_name'}]})


class TestGetDatasetCreateConfig:
    ALL_TYPES_DATA = {
        'str': pd.Series(['a', 'b'], dtype='str'),
        'bool': pd.Series([True, False], dtype='bool'),
        'int': pd.Series([1, 2], dtype='int'),
        'number': pd.Series([1.2, -4.3], dtype='float'),
        'datetime': pd.date_range("2022-10-27 10:50", periods=2, freq="H"),
        'datetimezone': pd.date_range("2022-10-27 10:50", periods=2, freq="H", tz="US/Pacific"),
        'mix': [1, 'a']
    }

    DATA_WITH_NA_VALUES = {
        'col1': pd.Series([None, 'b'], dtype='str'),
        'col2': pd.Series([1], dtype='int'),
    }

    def test_happy_path_get_dataset_config(self):
        all_types_df = pd.DataFrame(self.ALL_TYPES_DATA)
        dataset_create_config = get_dataset_config(all_types_df)
        assert is_dataset_create_config_valid(dataset_create_config)

        # validate columns types
        columns_types = [col['dataType']
                         for col in dataset_create_config['tableSchemaList'][0]['columns']]
        expected_column_types = ['Text', 'Logical', 'Int32',
                                 'Number', 'DateTime', 'DateTimeZone', 'Text']
        assert columns_types == expected_column_types

        # validate data rows
        rows = dataset_create_config['data'][0]['rows']
        expected_rows = [
            ['a', 'true', '1', '1.2', "2022-10-27 10:50:00",
                "2022-10-27 10:50:00-07:00", '1'],
            ['b', 'false', '2', '-4.3', "2022-10-27 11:50:00",
                "2022-10-27 11:50:00-07:00", 'a']
        ]
        assert rows == expected_rows

    def test_df_is_None(self):

        # Act + Assert
        with raises(Exception):
            get_dataset_config(None)

    def test_locale(self):
        dataset_create_config = get_dataset_config(
            pd.DataFrame([1, 2, 3]), locale='he-IL')
        assert dataset_create_config['locale'] == 'he-IL'

    def test_NAValuesInDataFrame(self):
        na_values_df = pd.DataFrame(self.DATA_WITH_NA_VALUES)
        dataset_create_config = get_dataset_config(na_values_df)
        assert is_dataset_create_config_valid(dataset_create_config)

    def test_duplicate_column_names(self):
        df = {
            'col1': pd.Series([None, 'b'], dtype='str'),
            'col2': pd.Series([1], dtype='int'),
            'col1': pd.Series([2], dtype='int'),
        }

        with pytest.raises(Exception):
            get_dataset_config(df)
