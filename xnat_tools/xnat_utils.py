import sys
import logging
import requests
import requests.packages.urllib3
import getpass

requests.packages.urllib3.disable_warnings()

_logger = logging.getLogger(__name__)


class XNATPass:

    DEFAULT = "Prompt if not specified"

    def __init__(self, value):
        if value == self.DEFAULT:
            value = getpass.getpass("XNAT Password: ")
        self.value = value

    def __str__(self):
        return self.value


def get(connection, url, **kwargs):
    try:
        r = connection.get(url, **kwargs)
        r.raise_for_status()
    except (requests.ConnectionError, requests.exceptions.RequestException) as e:
        _logger.critical("Request Failed\t%s", str(e))
        sys.exit(1)
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

    _logger.debug("------------------------------------------------")
    _logger.debug("Get project and subject information")
    r = get(
        connection,
        host + "/data/experiments/%s" % session,
        params={"format": "json", "handler": "values", "columns": "project,subject_ID"},
    )
    sessionValuesJson = r.json()["ResultSet"]["Result"][0]
    project = sessionValuesJson["project"]
    subjectID = sessionValuesJson["subject_ID"]
    _logger.debug("Project: " + project)
    _logger.debug("Subject ID: " + subjectID)

    r = get(
        connection,
        host + "/data/subjects/%s" % subjectID,
        params={"format": "json", "handler": "values", "columns": "label"},
    )
    subject = r.json()["ResultSet"]["Result"][0]["label"]
    _logger.debug("Subject label: " + subject)
    _logger.debug("------------------------------------------------")

    return project, subject


def get_scan_ids(connection, host, session):

    # Get list of scan ids
    _logger.info("------------------------------------------------")
    _logger.info(f"Get scans.")
    r = get(
        connection,
        host + "/data/experiments/%s/scans" % session,
        params={"format": "json"},
    )
    scanRequestResultList = sorted(
        r.json()["ResultSet"]["Result"], key=lambda x: int(x["ID"])
    )
    scanIDList = [scan["ID"] for scan in scanRequestResultList]
    seriesDescList = [
        scan["series_description"] for scan in scanRequestResultList
    ]  # { id: sd for (scan['ID'], scan['series_description']) in scanRequestResultList }
    _logger.debug("Found scans %s." % ", ".join(scanIDList))
    _logger.debug("Series descriptions %s" % ", ".join(seriesDescList))
    _logger.info("------------------------------------------------")

    return scanIDList, seriesDescList
