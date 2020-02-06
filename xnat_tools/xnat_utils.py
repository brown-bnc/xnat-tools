import os
import sys
import json
from shutil import copy as fileCopy
import requests
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

def get(connection, url, **kwargs):
    try:
        r = connection.get(url, **kwargs)
        r.raise_for_status()
    except (requests.ConnectionError, requests.exceptions.RequestException) as e:
        print("Request Failed")
        print("    " + str(e))
        sys.exit(1)
    return r


def download(connection, name, pathDict):
    if os.access(pathDict['absolutePath'], os.R_OK):
        print("We have local OS access")
        fileCopy(pathDict['absolutePath'], name)
        print('Copied %s.' % pathDict['absolutePath'])
    else:
        print('No accesess to local os %s.' % pathDict['absolutePath'])
        with open(name, 'wb') as f:
            r = get(connection, pathDict['URI'], stream=True)

            for block in r.iter_content(1024):
                if not block:
                    break

                f.write(block)
        print('Downloaded remote file %s.' % name)

def get_project_and_subject_id(connection, host, project, subject, session):
    """Get project ID and subject ID from session JSON
       If calling within XNAT, only session is passed"""
    print("Get project and subject ID for session ID %s." % session)
    r = get(connection, host + "/data/experiments/%s" % session, params={"format": "json", "handler": "values", "columns": "project,subject_ID"})
    sessionValuesJson = r.json()["ResultSet"]["Result"][0]
    project = sessionValuesJson["project"] if project is None else project
    subjectID = sessionValuesJson["subject_ID"]
    print("Project: " + project)
    print("Subject ID: " + subjectID)

    if subject is None:
        print()
        print("Get subject label for subject ID %s." % subjectID)
        r = get(connection, host + "/data/subjects/%s" % subjectID, params={"format": "json", "handler": "values", "columns": "label"})
        subject = r.json()["ResultSet"]["Result"][0]["label"]
        print("Subject label: " + subject)

    return project, subject

def get_scan_ids(connection, host, session):

    # Get list of scan ids
    print("Get scan list for session ID %s." % session)
    r = get(connection, host + "/data/experiments/%s/scans" % session, params={"format": "json"})
    scanRequestResultList = r.json()["ResultSet"]["Result"]
    scanIDList = [scan['ID'] for scan in scanRequestResultList]
    seriesDescList = [scan['series_description'] for scan in scanRequestResultList]  # { id: sd for (scan['ID'], scan['series_description']) in scanRequestResultList }
    print('Found scans %s.' % ', '.join(scanIDList))
    print('Series descriptions %s' % ', '.join(seriesDescList))

    # Fall back on scan type if series description field is empty
    if set(seriesDescList) == set(['']):
        seriesDescList = [scan['type'] for scan in scanRequestResultList]
        print('Fell back to scan types %s' % ', '.join(seriesDescList))

    return scanIDList, seriesDescList
