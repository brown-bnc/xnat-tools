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

import typer

from xnat_tools.bids_utils import (
    assign_bids_name,
    bidsmap_scans,
    correct_dicom_header,
    download_resources,
    path_string_preprocess,
    prepare_export_output_path,
    prepare_path_prefixes,
    validate_frame_counts,
)
from xnat_tools.logging import setup_logging
from xnat_tools.xnat_utils import (
    establish_connection,
    filter_scans,
    get_project_subject_session,
    get_scan_ids,
)

_logger = logging.getLogger(__name__)
app = typer.Typer()


@app.command()
def dicom_export(
    session: str = typer.Argument(
        ..., help="XNAT Session ID, that is the Accession # for an experiment."
    ),
    bids_root_dir: str = typer.Argument(..., help="Root output directory for exporting the files"),
    user: str = typer.Option(None, "-u", "--user", prompt=True, help="XNAT User"),
    password: str = typer.Option(
        None, "-p", "--pass", prompt=True, hide_input=True, help="XNAT Password"
    ),
    host: str = typer.Option("https://xnat.bnc.brown.edu", "-h", "--host", help="XNAT's URL"),
    session_suffix: str = typer.Option(
        "-1",
        "-S",
        "--session-suffix",
        help="The session_suffix is initially set to -1.\
              This will signify an unspecified session_suffix and default to sess-01.\
              For multi-session studies, the session label will be pulled from XNAT",
    ),
    bidsmap_file: str = typer.Option(
        "", "-f", "--bidsmap-file", help="Bidsmap JSON file to correct sequence names"
    ),
    includeseq: List[str] = typer.Option(
        [],
        "-i",
        "--includeseq",
        help="Include this sequence only, this flag can specify multiple times",
    ),
    skipseq: List[str] = typer.Option(
        [],
        "-s",
        "--skipseq",
        help="Exclude this sequence, this flag can specify multiple times",
    ),
    log_id: str = typer.Option(
        datetime.now().strftime("%m-%d-%Y-%H-%M-%S"),
        help="ID or suffix to append to logfile. If empty, current date is used",
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
    validate_frames: bool = typer.Option(
        False,
        "--validate_frames",
        help=(
            "Validate frame counts for all BOLD sequence acquisitions. "
            "Deletes the DICOM file if the final acquisition lacks expected slices."
        ),
    ),
    correct_dicoms_config: str = typer.Option(
        "", "-d", "--dicomfix-config", help="JSON file to correct DICOM fields. USE WITH CAUTION"
    ),
):

    """
    Export XNAT DICOM images in an experiment to a BIDS friendly format
    """
    bids_root_dir = os.path.expanduser(bids_root_dir)
    build_dir = os.getcwd()
    bidsmap = None

    # Parse bidsmap file
    if bidsmap_file:
        with Path(bidsmap_file).open() as f:
            bidsmap = json.load(f)

    # Set up working directory
    if not os.access(bids_root_dir, os.R_OK):
        raise ValueError(f"BIDS Root directory must exist: {bids_root_dir}")

    # Set up session
    connection = establish_connection(user, password)
    project, subject, session_suffix = get_project_subject_session(
        connection, host, session, session_suffix
    )

    project, subject, session_suffix = path_string_preprocess(project, subject, session_suffix)

    pi_prefix, study_prefix, subject_prefix, session_prefix = prepare_path_prefixes(
        project, subject, session_suffix
    )

    # Set up logging
    logs_dir = f"{bids_root_dir}/{pi_prefix}/{study_prefix}/logs"

    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir, exist_ok=True)

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

    # Download resources
    download_resources(connection, host, session, export_session_dir)

    assign_bids_name(
        connection,
        host,
        session,
        scans,
        build_dir,
        export_session_dir,
    )

    if validate_frames:
        validate_frame_counts(scans, export_session_dir)

    # If a configuration file is passed, correct DICOM headers of
    # specified files
    if correct_dicoms_config:
        correct_dicom_header(export_session_dir, correct_dicoms_config)

    # Close connection(I don't think this works)
    connection.delete(f"{host}/data/JSESSION")
    connection.close()

    return project, subject, session_suffix


def main():
    app()
