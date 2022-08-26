import requests  # type: ignore

from xnat_tools.xnat_utils import filter_scans, get


def phony_scan_data(scan_count=10):
    """Generates fake scan data to be used with filter_scans"""
    return [(f"{i}", f"Scan {i}") for i in range(1, scan_count + 1)]


def test_filter_scans():
    """Test filter_scans without a seqlist or a skiplist"""
    data = phony_scan_data()

    assert data == filter_scans(data)


def test_filter_scan_seqlist():
    """Test filter_scans with a seqlist"""
    data = phony_scan_data()
    seqlist = [2, 4, 6]

    result = filter_scans(data, seqlist=seqlist)
    expected_result = [x for x in data if int(x[0]) in seqlist]

    assert result == expected_result


def test_filter_scan_skiplist():
    """Test filter_scans with a skiplist"""
    data = phony_scan_data()
    skiplist = [2, 4, 6]

    result = filter_scans(data, skiplist=skiplist)
    expected_result = [x for x in data if int(x[0]) not in skiplist]

    assert result == expected_result


def test_filter_scan_seqlist_and_skiplist():
    """Test filter_scans with both a seqlist and a skiplist. Skiplist takes priority."""
    data = phony_scan_data()
    seqlist = [1, 2, 3, 4, 5]
    skiplist = [2, 4, 6]

    result = filter_scans(data, seqlist=seqlist, skiplist=skiplist)
    expected_result = [x for x in data if int(x[0]) in set(seqlist) - set(skiplist)]

    assert result == expected_result


def test_filter_scan_seqlist_discontinuity():
    """Test filter_scans when the scans have a discontinunity in ids"""
    data = phony_scan_data()

    # Delete the second element (index 1). Phony data should now be:
    #  [(1, "Scan 1"), (3, "Scan 3"), ...]
    del data[1]

    seqlist = [1, 2, 4]

    result = filter_scans(data, seqlist=seqlist)
    expected_result = [x for x in data if int(x[0]) in seqlist]

    assert result == expected_result


def test_unauthorized_user_exception_handling():
    """Test unauthorized user HTTPError response"""
    host = "https://xnat.bnc.brown.edu"
    session = "XNAT_E00114"
    url = f"{host}/data/experiments/{session}"

    user = "bad_user"
    password = "bad_password"

    connection = requests.Session()
    connection.verify = True
    connection.auth = (user, password)

    try:
        get(
            connection,
            url,
            params={"format": "json", "handler": "values", "columns": "project,subject_ID"},
        )
    except (requests.HTTPError) as e:
        assert e.response.status_code == 401
