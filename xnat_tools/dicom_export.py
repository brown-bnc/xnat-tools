"""
Filename: /dicom2bids.py
Path: xnat-dicom2bids-session
Created Date: Monday, August 26th 2019, 10:12:40 am
Maintainer: Isabel Restrepo
Description: Export a XNAT session into BIDS directory format


Original file lives here:
https://bitbucket.org/nrg_customizations/nrg_pipeline_dicomtobids/src/default/scripts/catalog/DicomToBIDS/scripts/dcm2bids_wholeSession.py
"""
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import List

import requests
import typer

from xnat_tools.bids_utils import (
    assign_bids_name,
    bidsmap_scans,
    prepare_bids_prefixes,
    prepare_export_output_path,
)
from xnat_tools.logging import setup_logging
from xnat_tools.xnat_utils import filter_scans, get_project_and_subject_id, get_scan_ids

_logger = logging.getLogger(__name__)
app = typer.Typer()


@app.command()
def dicom_export(
    session: str = typer.Argument(
        ..., help="XNAT Session ID, that is the Accession # for an experiment."
    ),
    bids_root_dir: str = typer.Argument(
        ..., help="Root output directory for exporting the files"
    ),
    user: str = typer.Option(None, "-u", "--user", prompt=True, help="XNAT User"),
    password: str = typer.Option(
        None, "-p", "--pass", prompt=True, hide_input=True, help="XNAT Password"
    ),
    host: str = typer.Option(
        "https://bnc.brown.edu/xnat", "-h", "--host", help="XNAT'sURL"
    ),
    session_suffix: str = typer.Option(
        "01",
        "S",
        "--session-suffix",
        help="Suffix of the session for BIDS defaults to 01. \
        This will produce a session label of sess-01. \
        You likely only need to change the default for multi-session studies",
    ),
    bidsmap_file: str = typer.Option(
        "", "-f", "--bidsmap-file", help="Bidsmap JSON file to correct sequence names"
    ),
    includeseq: List[int] = typer.Option(
        [],
        "-i",
        "--includeseq",
        help="Include this sequence only, can specify multiple times",
    ),
    skipseq: List[int] = typer.Option(
        [],
        "-s",
        "--skipseq",
        help="Exclude this sequence, can specify multiple times",
    ),
    log_id: str = typer.Option(
        datetime.now().strftime("%m-%d-%Y-%H-%M-%S"),
        help="ID or suffix to append to logfile, If empty, date is appended",
    ),
    verbose: int = typer.Option(
        0,
        "-v",
        "--verbose",
        count=True,
        help="Verbose level. Can be specified multiple times to increase verbosity",
    ),
    overwrite: bool = typer.Option(
        False,
        "--overwrite",
        help="Remove directories where prior results for session/participant may exist",
    ),
):

    """
    Export XNAT DICOM images in an experiment to a BIDS friendly format
    """
    bids_root_dir = os.path.expanduser(bids_root_dir)
    build_dir = os.getcwd()
    bidsmap = None

    # Parse bidsmap file
    if bidsmap_file != "":
        with Path(bidsmap_file).open() as f:
            bidsmap = json.load(f)

    # Set up working directory
    if not os.access(bids_root_dir, os.R_OK):
        raise ValueError(f"BIDS Root directory must exist: {bids_root_dir}")

    # Set up session
    connection = requests.Session()
    connection.verify = True
    connection.auth = (user, password)

    project, subject = get_project_and_subject_id(connection, host, session)

    pi_prefix, study_prefix, subject_prefix, session_prefix = prepare_bids_prefixes(
        project, subject, session_suffix
    )

    # Set up logging
    logs_dir = f"{bids_root_dir}/{pi_prefix}/{study_prefix}/logs"

    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    setup_logging(_logger, f"{logs_dir}/export-{log_id}.log", verbose_level=verbose)

    export_session_dir = prepare_export_output_path(
        bids_root_dir,
        pi_prefix,
        study_prefix,
        subject_prefix,
        session_prefix,
        overwrite=overwrite,
    )

    # Export
    scans = get_scan_ids(connection, host, session)
    scans = filter_scans(scans, seqlist=includeseq, skiplist=skipseq)
    scans = bidsmap_scans(scans, bidsmap)

    assign_bids_name(
        connection,
        host,
        subject,
        session,
        scans,
        build_dir,
        export_session_dir,
    )

    # Close connection(I don't think this works)
    connection.delete(f"{host}/data/JSESSION")
    connection.close()

    return project, subject


def main():
    app()
