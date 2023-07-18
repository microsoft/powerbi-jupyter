import requests_mock
from ..report import Report

EMBED_URL = 'dummy_embed_url'
GROUP_ID = 'dummy_group_id'
REPORT_ID = 'dummy_report_id'
INITIAL_REPORT_ID = 'dummy_initial_report_id'
ACCESS_TOKEN = 'dummy_access_token'

def create_test_report(embedded=True, permissions=None):
    with requests_mock.Mocker() as rm:
        request_url = f"https://api.powerbi.com/v1.0/myorg/groups/{GROUP_ID}/reports/{REPORT_ID}"
        rm.get(request_url, json={ 'embedUrl': f"{EMBED_URL}/groups/{GROUP_ID}/reports/{REPORT_ID}" })
        report_mock = Report(group_id=GROUP_ID, report_id=REPORT_ID, auth=ACCESS_TOKEN, permissions=permissions)
        report_mock._embedded = embedded
        return report_mock