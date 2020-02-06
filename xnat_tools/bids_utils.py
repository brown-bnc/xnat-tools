import json
import os
import collections
import six
from six.moves import zip
from xnat_utils import get, download

def prepare_bids_prefixes(project, subject, session):
    #get PI from project name
    pi_prefix = project.lower().split('_')[0] 

     # Paths to export source data in a BIDS friendly way
    study_prefix = "study-" + project.lower().split('_')[1]
    subject_prefix = "sub-" + subject.lower()
    session_prefix = "ses-"+ session.lower()

    return pi_prefix, study_prefix, subject_prefix, session_prefix

def prepare_bids_output_path(bids_root_dir, pi_prefix, study_prefix, subject_prefix, session_prefix):

    bids_study_dir = os.path.join(bids_root_dir, pi_prefix, study_prefix)
    bids_subject_dir = os.path.join(bids_study_dir, "xnat-export", subject_prefix)
    bids_session_dir = os.path.join(bids_subject_dir, session_prefix)

    # Set up working directory
    if not os.access(bids_session_dir, os.R_OK):
        print('Making output BIDS Session directory %s' % bids_study_dir)
        os.makedirs(bids_session_dir)

    return bids_session_dir

def prepare_heudi_prefixes(project, subject, session):
    #get PI from project name
    pi_prefix = project.lower().split('_')[0] 

     # Paths to export source data in a BIDS friendly way
    study_prefix = "study-" + project.lower().split('_')[1]
    subject_prefix = subject.lower()
    session_prefix = session.lower()

    return pi_prefix, study_prefix, subject_prefix, session_prefix

def prepare_heudiconv_output_path(bids_root_dir, pi_prefix, study_prefix, subject_prefix, session_prefix):

    heudi_study_dir = os.path.join(bids_root_dir, pi_prefix, study_prefix)
    heudi_output_dir = os.path.join(heudi_study_dir, "bids")

    # Set up working directory
    if not os.access(heudi_output_dir, os.R_OK):
        print('Making output BIDS Session directory %s' % heudi_output_dir)
        os.makedirs(heudi_output_dir)

    return heudi_output_dir

def populate_bidsmap(connection, host, project, seriesDescList):
    # Read bids map from input config
    bidsmaplist = []

    print("Get project BIDS map if one exists")
    # We don't use the convenience get() method because that throws exceptions when the object is not found.
    r = connection.get(host + "/data/projects/%s/resources/config/files/bidsmap.json" % project, params={"contents": True})
    if r.ok:
        bidsmaptoadd = r.json()
        print("BIDS bidsmaptoadd: ",  bidsmaptoadd)
        for mapentry in bidsmaptoadd:
            if mapentry not in bidsmaplist:
                bidsmaplist.append(mapentry)
    else:
        print("Could not read project BIDS map")


    # Get site-level configs
    print("Get Site BIDS map ")
    # We don't use the convenience get() method because that throws exceptions when the object is not found.
    r = connection.get(host + "/data/config/bids/bidsmap", params={"contents": True})
    if r.ok:
        bidsmaptoadd = r.json()
        print("BIDS bidsmaptoadd: ",  bidsmaptoadd)
        for mapentry in bidsmaptoadd:
            if mapentry not in bidsmaplist:
                bidsmaplist.append(mapentry)
    else:
        print("Could not read site-wide BIDS map")

    print("BIDS bidsmaplist: ", json.dumps(bidsmaplist))

    # Collapse human-readable JSON to dict for processing
    bidsnamemap = {x['series_description'].lower(): x['bidsname'] for x in bidsmaplist if 'series_description' in x and 'bidsname' in x}

    # Map all series descriptions to BIDS names (case insensitive)
    resolved = [bidsnamemap[x.lower()] for x in seriesDescList if x.lower() in bidsnamemap]

    # Count occurrences
    bidscount = collections.Counter(resolved)

    # Remove multiples
    multiples = {seriesdesc: count for seriesdesc, count in six.viewitems(bidscount) if count > 1}

    return bidsnamemap

def assign_bids_name(connection, host, subject, session, scanIDList, seriesDescList, build_dir, bids_session_dir, bidsnamemap):
    """
        subject: Subject to process
        scanIDList: ID List of scans 
        seriesDescList: List of series descriptions
        build_dir: build director. What is this?
        study_bids_dir: BIDS directory to copy simlinks to. Typically the RESOURCES/BIDS
    """

    # Cheat and reverse scanid and seriesdesc lists so numbering is in the right order
    for scanid, seriesdesc in zip(reversed(scanIDList), reversed(seriesDescList)):

        print('Beginning process for scan %s.' % scanid)
        os.chdir(build_dir)
        print('Assigning BIDS name for scan %s.' % scanid)

        #We use the bidsmap to correct miss-labeled series at the scanner.
        #otherwise we assume decription is correct and let heudiconv tdo the work
        if seriesdesc.lower() not in bidsnamemap:
            print("Series " + seriesdesc + " not found in BIDSMAP")
            # bidsname = "Z"
            # continue  # Exclude series from processing
            match = seriesdesc.lower()
        else:
            print("Series " + seriesdesc + " matched " + bidsnamemap[seriesdesc.lower()])
            match = bidsnamemap[seriesdesc.lower()]

        bidsname = match

        # Get scan resources
        print("Get scan resources for scan %s." % scanid)
        r = get(connection, host + "/data/experiments/%s/scans/%s/resources" % (session, scanid), params={"format": "json"})
        scanResources = r.json()["ResultSet"]["Result"]
        print('Found resources %s.' % ', '.join(res["label"] for res in scanResources))

        dicomResourceList = [res for res in scanResources if res["label"] == "DICOM"]

        if len(dicomResourceList) == 0:
            print("Scan %s has no DICOM resource." % scanid)
            # scanInfo['hasDicom'] = False
            continue
        elif len(dicomResourceList) > 1:
            print("Scan %s has more than one DICOM resource Skipping." % scanid)
            # scanInfo['hasDicom'] = False
            continue

        dicomResource = dicomResourceList[0] if len(dicomResourceList) > 0 else None

        usingDicom = True if (len(dicomResourceList) == 1) else False

        if dicomResource is not None and dicomResource["file_count"]:
            if int(dicomResource["file_count"]) == 0:
                print("DICOM resource for scan %s has no files. Skipping." % scanid)
                continue
        else:
            print("DICOM resources for scan %s have a blank \"file_count\", so I cannot check to see if there are no files. I am not skipping the scan, but this may lead to errors later if there are no files." % scanid)

        # BIDS sourcedatadirectory for this scan
        print("bids_session_dir: ", bids_session_dir)
        print("bidsname: ", bidsname)
        bids_scan_directory = os.path.join(bids_session_dir, bidsname)

        if not os.path.isdir(bids_scan_directory):
            print('Making scan DICOM directory %s.' % bids_scan_directory)
            os.mkdir(bids_scan_directory)
        
        # For now exit if directory is not empty
        for f in os.listdir(bids_scan_directory):
            print("Output Directory is not empty. Skipping.")
            continue
            # os.remove(os.path.join(bids_scan_directory, f))

        # Deal with DICOMs
        print('Get list of DICOM files for scan %s.' % scanid)

        if usingDicom:
            filesURL = host + "/data/experiments/%s/scans/%s/resources/DICOM/files" % (session, scanid)
        
        r = get(connection, filesURL, params={"format": "json"})
        # Build a dict keyed off file name
        dicomFileDict = {dicom['Name']: {'URI': host + dicom['URI']} for dicom in r.json()["ResultSet"]["Result"]}

        print("**********")
        print(dicomFileDict)
        print("**********")

        # Have to manually add absolutePath with a separate request
        r = get(connection, filesURL, params={"format": "json", "locator": "absolutePath"})
        for dicom in r.json()["ResultSet"]["Result"]:
            dicomFileDict[dicom['Name']]['absolutePath'] = dicom['absolutePath']

        # Download DICOMs
        print("Downloading files for scan %s." % scanid)
        os.chdir(bids_scan_directory)

        # Check secondary
        # Download any one DICOM from the series and check its headers
        # If the headers indicate it is a secondary capture, we will skip this series.
        dicomFileList = list(dicomFileDict.items())

        (name, pathDict) = dicomFileList[0]
        download(connection, name, pathDict)

        # Download remaining DICOMs
        for name, pathDict in dicomFileList[1:]:
            download(connection, name, pathDict) 

        os.chdir(build_dir)
        print('Done downloading for scan %s.' % scanid)
    

