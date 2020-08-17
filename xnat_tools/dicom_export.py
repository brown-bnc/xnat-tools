"""
Filename: /dicom2bids.py
Path: xnat-dicom2bids-session
Created Date: Monday, August 26th 2019, 10:12:40 am
Maintainer: Isabel Restrepo
Description: Export a XNAT session into BIDS directory format


Original file lives here: https://bitbucket.org/nrg_customizations/nrg_pipeline_dicomtobids/src/default/scripts/catalog/DicomToBIDS/scripts/dcm2bids_wholeSession.py
"""

import argparse
import coloredlogs
import json
import logging
import os
import requests
import sys

from datetime import datetime
from pathlib import Path

from xnat_tools.bids_utils import (
    assign_bids_name,
    bidsmap_scans,
    populate_bidsmap,
    prepare_bids_prefixes,
    prepare_export_output_path,
)

from xnat_tools.xnat_utils import (
    filter_scans,
    get_project_and_subject_id,
    get_scan_ids,
)

_logger = logging.getLogger(__name__)


def parse_args(args):
    """Parse command line parameters

    Args:
      args ([str]): command line parameters as list of strings

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(
        description="Dump XNAT Session into a BIDS friendly directory"
    )
    parser.add_argument("--host", default="https://bnc.brown.edu/xnat", help="Host")
    parser.add_argument("-u", "--user", help="XNAT username", required=True)
    parser.add_argument(
        "-p",
        "--password",
        type=XNATPass,
        help="XNAT password",
        default=XNATPass.DEFAULT,
    )
    parser.add_argument("--session", help="Session ID", required=True)
    parser.add_argument(
        "--session_suffix",
        help="Suffix of the session for BIDS e.g, 01. This will produce a sesstion label of sess-01",
        required=True,
        type=str,
    )
    parser.add_argument(
        "--bids_root_dir", help="Root output directory for BIDS files", required=True
    )
    parser.add_argument(
        "--bidsmap_file",
        help="Bidsmap JSON file to correct sequence names",
        required=False,
        default="",
    )
    parser.add_argument(
        "--seqlist",
        help="List of sequences from XNAT to run if don't want to process all seuqences",
        required=False,
        default=[],
        nargs="*",  # 0 or more values expected => creates a list
        type=int,
    )
    parser.add_argument(
        "--skiplist",
        help="List of sequences from XNAT to SKIP. Accepts a list --skiplist 1 2 3",
        required=False,
        default=[],
        nargs="*",  # 0 or more values expected => creates a list
        type=int,
    )
    parser.add_argument(
        "--log_id",
        help="ID or suffix to append to logfile, If empty, date is appended",
        required=False,
        default=datetime.now().strftime("%m-%d-%Y-%H-%M-%S"),
        type=str,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        help="set loglevel to INFO",
        action="store_const",
        const=logging.INFO,
    )
    parser.add_argument(
        "-vv",
        "--very-verbose",
        dest="loglevel",
        help="set loglevel to DEBUG",
        action="store_const",
        const=logging.DEBUG,
    )
    parser.add_argument(
        "--overwrite",
        help="Remove directories where prior results for session/participant may exist",
        action="store_true",
        default=False,
    )

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
        handlers=[logging.FileHandler(logfile), logging.StreamHandler(sys.stdout)],
    )
    coloredlogs.install(level=loglevel, logger=_logger)


def main(args):
    """Main entry point allowing external calls

    Args:
      args ([namespase]): command line parameter list
    """
    host = args.host
    session = args.session
    session_suffix = args.session_suffix
    bidsmap_file = args.bidsmap_file
    bids_root_dir = os.path.expanduser(args.bids_root_dir)

    build_dir = os.getcwd()
    seqlist = args.seqlist
    skiplist = args.skiplist
    log_id = args.log_id
    overwrite = args.overwrite
    bidsmap = None

    # Parse bidsmap file
    if args.bidsmap_file:
        bidsmap_file = Path(args.bidsmap_file)
        if not bidsmap_file.exists():
            _logger.info("BIDSMAP file does not exist or wasn't passed")
        else:
            with bidsmap_file.open() as f:
                bidsmap = json.load(f)

    # Set up working directory
    if not os.access(bids_root_dir, os.R_OK):
        raise ValueError(f"BIDS Root directory must exist: {bids_root_dir}")

    # Set up session
    connection = requests.Session()
    connection.verify = False
    connection.auth = (args.user, args.password)

    project, subject = get_project_and_subject_id(connection, host, session)

    pi_prefix, study_prefix, subject_prefix, session_prefix = prepare_bids_prefixes(
        project, subject, session_suffix
    )

    # Set up logging
    logs_dir = f"{bids_root_dir}/{pi_prefix}/{study_prefix}/logs"

    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    setup_logging(args.loglevel, f"{logs_dir}/export-{log_id}.log")

    export_session_dir = prepare_export_output_path(
        bids_root_dir,
        pi_prefix,
        study_prefix,
        subject_prefix,
        session_prefix,
        overwrite,
    )

    scans = get_scan_ids(connection, host, session)
    scans = filter_scans(scans, seqlist=seqlist, skiplist=skiplist)
    scans = bidsmap_scans(scans, bidsmap)

    # Prepare files for heudiconv
    assign_bids_name(
        connection,
        host,
        subject,
        session,
        scans,
        build_dir,
        export_session_dir,
    )

    connection.delete(f"{host}/data/JSESSION")
    connection.close()

    return 0


def run():
    """Entry point for console scripts
    """
    args = parse_args(sys.argv[1:])
    code = main(args)
    return code


if __name__ == "__main__":
    run()
