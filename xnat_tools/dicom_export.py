'''
Filename: /dicom2bids.py
Path: xnat-dicom2bids-session
Created Date: Monday, August 26th 2019, 10:12:40 am
Maintainer: Isabel Restrepo
Descriptyion: Export a XNAT session into BIDS directory format


Original file lives here: https://bitbucket.org/nrg_customizations/nrg_pipeline_dicomtobids/src/default/scripts/catalog/DicomToBIDS/scripts/dcm2bids_wholeSession.py
'''

import argparse
import coloredlogs, logging

import os
import sys
import tempfile


from xnat_tools.bids_utils import *
from xnat_tools.xnat_utils import *

_logger = logging.getLogger(__name__)

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
        description="Dump XNAT Session into a BIDS friendly directory")
    parser.add_argument(
        "--host",
        default="https://bnc.brown.edu/xnat",
        help="Host")
    parser.add_argument(
        "-u", "--user",
        help="XNAT username",
        required=True)
    parser.add_argument(
        '-p', '--password',
        type=XNATPass,
        help='XNAT password',
        default=XNATPass.DEFAULT)
    parser.add_argument(
        "--session",
        help="Session ID",
        required=True)
    parser.add_argument(
        "--bids_root_dir",
        help="Root output directory for BIDS files",
        required=True)
    parser.add_argument(
        "--bidsmap_file",
        help="Bidsmap JSON file to correct sequence names",
        required=False,
        default="")
    parser.add_argument(
        "--seqlist",
        help="List of sequences from XNAT to run if don't want to process all seuqences",
        required=False,
        default=[],
        nargs="*",  # 0 or more values expected => creates a list
        type=int)
    parser.add_argument(
        "--skiplist",
        help="List of sequences from XNAT to SKIP. Accepts a list --skiplist 1 2 3",
        required=False,
        default=[],
        nargs="*",  # 0 or more values expected => creates a list
        type=int)
    parser.add_argument(
        '-v',
        '--verbose',
        dest="loglevel",
        help="set loglevel to INFO",
        action='store_const',
        const=logging.INFO)
    parser.add_argument(
        '-vv',
        '--very-verbose',
        dest="loglevel",
        help="set loglevel to DEBUG",
        action='store_const',
        const=logging.DEBUG)

    args, _ = parser.parse_known_args(args)
    return args

def setup_logging(loglevel, logfile):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    if loglevel is None:
        loglevel = logging.INFO
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel, 
        format=logformat, 
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(logfile),
            logging.StreamHandler(sys.stdout)
        ]
    )


def main(args):
    """Main entry point allowing external calls

    Args:
      args ([namespase]): command line parameter list
    """
    host = args.host
    session = args.session
    bidsmap_file = args.bidsmap_file
    bids_root_dir = os.path.expanduser(args.bids_root_dir)

    build_dir = os.getcwd()
    seqlist = args.seqlist
    skiplist = args.skiplist

    # Set up working directory
    if not os.access(bids_root_dir, os.R_OK):
        raise ValueError(f"BIDS Root directory must exist: {bids_root_dir}")

    # Set up session
    connection = requests.Session()
    connection.verify = False
    connection.auth = (args.user, args.password)
    
    project, subject = get_project_and_subject_id(connection, host, session)
    
    pi_prefix, study_prefix, subject_prefix, session_prefix = prepare_bids_prefixes(project, subject, session)

    # Set up logging
    logs_dir = f"{bids_root_dir}/{pi_prefix}/{study_prefix}/logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    setup_logging(args.loglevel, logs_dir + "/xnat_export.log")
    coloredlogs.install()

    bids_session_dir = prepare_bids_output_path(bids_root_dir, pi_prefix, study_prefix, subject_prefix, session_prefix)
    
    scanIDList, seriesDescList = get_scan_ids(connection, host, session)

    if seqlist != []:
        scanIDList = [scanIDList[i-1] for i in seqlist]
        seriesDescList = [seriesDescList[i-1] for i in seqlist]

    if skiplist != []:
        scanIDList = [scanIDList[i] for i, idx in enumerate(scanIDList) if int(idx) not in skiplist ]
        seriesDescList = [seriesDescList[i-1] for i,idx in enumerate(scanIDList) if int(idx) not in skiplist]

    _logger.info("---------------------------------")
    _logger.info("Processing Series: ")
    for s in seriesDescList:
        _logger.info(s)
    _logger.info("---------------------------------")


    # Prepare files for heudiconv
    bidsnamemap = populate_bidsmap(bidsmap_file, seriesDescList)
    assign_bids_name(connection, host, subject, session, scanIDList, seriesDescList, build_dir, bids_session_dir, bidsnamemap)

    connection.delete(f"{host}/data/JSESSION")
    connection.close()

def run():
    """Entry point for console scripts
    """
    args = parse_args(sys.argv[1:])
    main(args)


if __name__ == "__main__":
    run()