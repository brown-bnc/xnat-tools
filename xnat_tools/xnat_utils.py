import getpass
import logging

import urllib3

urllib3.disable_warnings()

_logger = logging.getLogger(__name__)


class XNATPass:

    DEFAULT = "Prompt if not specified"

    def __init__(self, value=DEFAULT):
        if value == self.DEFAULT:
            value = getpass.getpass("XNAT Password: ")
        self.value = value

    def __str__(self):
        return self.value


def get(connection, url, **kwargs):
    r = connection.get(url, **kwargs)
    r.raise_for_status()

    return r


def download(connection, name, pathDict):

    with open(name, "wb") as f:
        r = get(connection, pathDict["URI"], stream=True)

        for block in r.iter_content(1024):
            if not block:
                break

            f.write(block)
    _logger.debug("Downloaded remote file %s." % name)


def get_project_and_subject_id(connection, host, session):
    """Get project ID and subject ID from session JSON
    If calling within XNAT, only session is passed"""

    print("------------------------------------------------")
    print("Get project and subject information")
    r = get(
        connection,
        host + "/data/experiments/%s" % session,
        params={"format": "json", "handler": "values", "columns": "project,subject_ID"},
    )
    sessionValuesJson = r.json()["ResultSet"]["Result"][0]
    project = sessionValuesJson["project"]
    subjectID = sessionValuesJson["subject_ID"]
    print("Project: " + project)
    print("Subject ID: " + subjectID)

    r = get(
        connection,
        host + "/data/subjects/%s" % subjectID,
        params={"format": "json", "handler": "values", "columns": "label"},
    )
    subject = r.json()["ResultSet"]["Result"][0]["label"]
    print("Subject label: " + subject)
    print("------------------------------------------------")

    return project, subject


def get_scan_ids(connection, host, session):

    # Get list of scan ids
    _logger.info("------------------------------------------------")
    _logger.info("Get scans.")
    r = get(
        connection,
        host + "/data/experiments/%s/scans" % session,
        params={"format": "json"},
    )
    scanRequestResultList = sorted(r.json()["ResultSet"]["Result"], key=lambda x: int(x["ID"]))
    scanIDList = [scan["ID"] for scan in scanRequestResultList]
    seriesDescList = [
        scan["series_description"] for scan in scanRequestResultList
    ]  # { id: sd for (scan['ID'], scan['series_description']) in scanRequestResultList }
    _logger.debug("Found scans %s." % ", ".join(scanIDList))
    _logger.debug("Series descriptions %s" % ", ".join(seriesDescList))
    _logger.info("------------------------------------------------")

    return list(zip(scanIDList, seriesDescList))


def filter_scans(scans, seqlist=[], skiplist=[]):
    """Filters the scans based on the sequence list and the skip list"""
    if not seqlist and not skiplist:
        return scans

    if not seqlist:
        desired_scans = scans
    else:
        desired_scans = [scan for scan in scans if int(scan[0]) in seqlist]

    desired_scans = [scan for scan in desired_scans if int(scan[0]) not in skiplist]

    return desired_scans
