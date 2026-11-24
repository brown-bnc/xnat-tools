import requests

from xnat_tools.xnat_utils import establish_connection, get


def test_unauthorized_user_exception_handling(xnat_host, test_session):
    """Test unauthorized user HTTPError response"""

    session_data, _, _ = test_session
    _, _, session, _ = session_data

    connection = establish_connection("base_user", "bad_password")
    url = f"{xnat_host}/data/experiments/{session}"
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

    session = "XNAT_BAD_PROJECT"

    connection = establish_connection(xnat_user, xnat_password)
    url = f"{xnat_host}/data/experiments/{session}"
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
        assert e.response is not None and e.response.status_code == 404
