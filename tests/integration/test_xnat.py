import requests

from xnat_tools.xnat_utils import establish_connection, get


def test_unauthorized_user_exception_handling(xnat_host):
    """Test unauthorized user HTTPError response"""
    session = "XNAT_E00114"
    url = f"{xnat_host}/data/experiments/{session}"
    user = "bad_user"
    password = "bad_password"

    connection = establish_connection(user, password)

    try:
        get(
            connection,
            url,
            params={
                "format": "json",
                "handler": "values",
                "columns": "project,subject_ID",
            },
        )
    except requests.HTTPError as e:
        assert e.response is not None and e.response.status_code == 401


def test_xnat_reachable_exception_handling(xnat_host, xnat_user, xnat_password):
    """Test unauthorized user HTTPError response"""
    session = "XNAT_BADPROJECT"
    url = f"{xnat_host}/data/experiments/{session}"

    connection = establish_connection(xnat_user, xnat_password)

    try:
        get(
            connection,
            url,
            params={
                "format": "json",
                "handler": "values",
                "columns": "project,subject_ID",
            },
        )
    except requests.HTTPError as e:
        assert e.response and e.response.status_code == 404
