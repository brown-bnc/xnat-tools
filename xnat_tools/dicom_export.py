'''
Filename: xnat2bids-heudiconv/dicom_simlink_dump.py
Created Date: Friday, December 6th 2019, 2:28:10 pm
Author: Isabel Restrepo

Export XNAT DICOM SCANS as symlinks to the Resources folder for BIDS

Copyright (c) 2019 Brown University
'''

'''
Filename: /dicom2bids.py
Path: xnat-dicom2bids-session
Created Date: Monday, August 26th 2019, 10:12:40 am
Maintainer: Isabel Restrepo
Descriptyion: Export a XNAT session into BIDS directory format


Original file lives here: https://bitbucket.org/nrg_customizations/nrg_pipeline_dicomtobids/src/default/scripts/catalog/DicomToBIDS/scripts/dcm2bids_wholeSession.py
'''

import argparse
import logging


import os
import sys
import tempfile


from bids_utils import *
from xnat_utils import *


_logger = logging.getLogger(__name__)

# def cleanServer(server):
#     server.strip()
#     if server[-1] == '/':
#         server = server[:-1]
#     if server.find('http') == -1:
#         server = 'https://' + server
#     return server


def isTrue(arg):
    return arg is not None and (arg == 'Y' or arg == '1' or arg == 'True')

def parse_args(args):
    """Parse command line parameters

    Args:
      args ([str]): command line parameters as list of strings

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(
        description="Dump DICOMS to a BIDS firendly sourcedata directory")
    parser.add_argument(
        "--host",
        default="http://bnc.brown.edu/xnat-dev",
        help="DEV host",
        required=True)
    parser.add_argument(
        "--user",
        help="CNDA username",
        required=True)
    parser.add_argument(
        "--password",
        help="Password",
        required=True)
    parser.add_argument(
        "--session",
        help="Session ID",
        required=True)
    parser.add_argument(
        "--subject",
        help="Subject Label",
        required=False)
    parser.add_argument(
        "--project",
        help="Project",
        required=False)
    parser.add_argument(
        "--bids_root_dir",
        help="Root output directory for BIDS files",
        required=True)
    # parser.add_argument("--overwrite", help="Overwrite NIFTI files if they exist")
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1')

    return parser.parse_args(args)

    

def main(args):
    """Main entry point allowing external calls

    Args:
      args ([str]): command line parameter list
    """
    args = parse_args(args)

    host = args.host
    session = args.session
    subject = args.subject
    project = args.project
    # overwrite = isTrue(args.overwrite)
    # dicomdir = args.dicomdir
    bids_root_dir = args.bids_root_dir
    build_dir = os.getcwd()

    # Set up working directory
    if not os.access(bids_root_dir, os.R_OK):
        raise ValueError(f"BIDS Root directory must exist: {bids_root_dir}")
        # print('Making BIDS directory %s' % bids_root_dir)
        # os.mkdir(bids_root_dir)

    # Set up session
    connection = requests.Session()
    connection.verify = False
    connection.auth = (args.user, args.password)
    
    if project is None or subject is None:
        project, subject = get_project_and_subject_id(connection, host, project, subject, session)
    
    scanIDList, seriesDescList = get_scan_ids(connection, host, session)
    
    pi_prefix, study_prefix, subject_prefix, session_prefix = prepare_bids_prefixes(project, subject, session)

    bids_session_dir = prepare_bids_output_path(bids_root_dir, pi_prefix, study_prefix, subject_prefix, session_prefix)
    
    # Prepare files for heudiconv
    bidsnamemap = populate_bidsmap(connection, host, project, seriesDescList)
    assign_bids_name(connection, host, subject, session, scanIDList, seriesDescList, build_dir, bids_session_dir, bidsnamemap)


def run():
    """Entry point for console_scripts
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    run()