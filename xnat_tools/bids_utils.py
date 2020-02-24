import json
import os
import collections
import six
import pydicom
from six.moves import zip
from xnat_tools.xnat_utils import get, download

def prepare_bids_prefixes(project, subject, session):
    #get PI from project name
    pi_prefix = project.lower().split('_')[0] 

     # Paths to export source data in a BIDS friendly way
    study_prefix = "study-" + project.lower().split('_')[1]
    subject_prefix = "sub-" + subject.lower().replace("_","")
    session_prefix = "ses-"+ session.lower().replace("_","")

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
    subject_prefix = subject.lower().replace("_","")
    session_prefix = session.lower().replace("_","")

    return pi_prefix, study_prefix, subject_prefix, session_prefix

def prepare_heudiconv_output_path(bids_root_dir, pi_prefix, study_prefix, subject_prefix, session_prefix):

    heudi_study_dir = os.path.join(bids_root_dir, pi_prefix, study_prefix)
    heudi_output_dir = os.path.join(heudi_study_dir, "bids")

    # Set up working directory
    if not os.access(heudi_output_dir, os.R_OK):
        print('Making output BIDS Session directory %s' % heudi_output_dir)
        os.makedirs(heudi_output_dir)

    return heudi_output_dir

def populate_bidsmap(bidsmap_file, seriesDescList):
    # Read bids map from input config
    bidsmaplist = []

    print("Read bidsmap file if one exists")
    
    if os.path.exists(bidsmap_file):
        with open(bidsmap_file) as json_file:
            bidsmaptoadd = json.load(json_file)
            print("BIDS bidsmaptoadd: ",  bidsmaptoadd)
            for mapentry in bidsmaptoadd:
                if mapentry not in bidsmaplist:
                    bidsmaplist.append(mapentry)


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

def handle_scanner_exceptions(match):
    # T1W and T2W need to be upper case
    match = match.replace("t1w", "T1w")
    match = match.replace("t2w", "T2w")

    # Handle the aascout planes
    match = match.replace("_mpr_sag", "-mpr-sag")
    match = match.replace("_mpr_cor", "-mpr-cor")
    match = match.replace("_mpr_tra", "-mpr-tra") 

    # Handle the mprage rms
    match = match.replace(" rms", "-rms")

    return match

def detect_multiple_runs(seriesDescList):
    
    dups = {}

    # Make series descriptions unique by appending _run- to non-unique ones
    for i, val in enumerate(seriesDescList):
        if val not in dups:
            # Store index of first occurrence and occurrence value
            dups[val] = [i, 1]
        else:
            # Special case for first occurrence
            if dups[val][1] == 1:
                run_idx = dups[val][1]
                seriesDescList[dups[val][0]] += f"_run-{run_idx}"

            # Increment occurrence value, index value doesn't matter anymore
            dups[val][1] += 1

            # Use stored occurrence value
            run_idx = dups[val][1]
            seriesDescList[i] += f"_run-{run_idx}"

    return seriesDescList

def bidsify_dicom_headers(filename, protocol_name):

    dataset = pydicom.dcmread(filename)

    if 'ProtocolName' in dataset:
        if dataset.data_element('ProtocolName').value != protocol_name:
            print("Modifying DICOM Header for ProtocolName from")
            print(f"{dataset.data_element('ProtocolName').value} to {protocol_name}")
            dataset.data_element('ProtocolName').value = protocol_name
            print("Modifying DICOM Header for SeriesDescription from")
            print(f"{dataset.data_element('SeriesDescription').value} to {protocol_name}")
            dataset.data_element('SeriesDescription').value = protocol_name
            dataset.save_as(filename)


def assign_bids_name(connection, host, subject, session, scanIDList, seriesDescList, build_dir, bids_session_dir, bidsnamemap):
    """
        subject: Subject to process
        scanIDList: ID List of scans 
        seriesDescList: List of series descriptions
        build_dir: build director. What is this?
        study_bids_dir: BIDS directory to copy simlinks to. Typically the RESOURCES/BIDS
    """

    # Detect duplicate sequences, assume they are runs
    # seriesDescList = detect_multiple_runs(seriesDescList)

    # Cheat and reverse scanid and seriesdesc lists so numbering is in the right order
    for scanid, seriesdesc in zip(reversed(scanIDList), reversed(seriesDescList)):

        print(f"Assigning BIDS name for scan {scanid}:{seriesdesc}")
        os.chdir(build_dir)

        #We use the bidsmap to correct miss-labeled series at the scanner.
        #otherwise we assume decription is correct and let heudiconv do the work
        if seriesdesc.lower() not in bidsnamemap:
            print("Series " + seriesdesc + " not found in BIDSMAP")
            # bidsname = "Z"
            # continue  # Exclude series from processing
            match = seriesdesc.lower()

        else:
            print("Series " + seriesdesc + " matched " + bidsnamemap[seriesdesc])
            match = bidsnamemap[seriesdesc]

        match = handle_scanner_exceptions(match)
        bidsname = match
        

        print(f"****BIDSNAME*****: {bidsname}")

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
        dicomFileList = list(dicomFileDict.items())
        (name, pathDict) = dicomFileList[0]
        download(connection, name, pathDict)

        bidsify_dicom_headers(name, bidsname)

        # Download remaining DICOMs
        for name, pathDict in dicomFileList[1:]:
            download(connection, name, pathDict) 
            bidsify_dicom_headers(name, bidsname)


        os.chdir(build_dir)
        print('Done downloading for scan %s.' % scanid)
    

