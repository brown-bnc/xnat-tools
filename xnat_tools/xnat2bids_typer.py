import os
import json
import requests
from datetime import datetime
from pathlib import Path

import logging

import typer
from typing import List, Optional

from xnat_tools.logging import setup_logging

from xnat_tools.bids_utils import (
    assign_bids_name,
    bidsmap_scans,
    prepare_bids_prefixes,
    prepare_export_output_path,
)

from xnat_tools.xnat_utils import (
    filter_scans,
    get_project_and_subject_id,
    get_scan_ids,
)

# from xnat_tools.xnat_utils import XNATPass
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
        "-ss",
        "--session-suffix",
        help="Suffix of the session for BIDS defaults to 01. This will produce a session label of sess-01. You likely only need to change the dault for multi-session studies",
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
        [], "-s", "--skipseq", help="Exclude this sequence, can specify multiple times",
    ),
    log_id: str = typer.Option(
        datetime.now().strftime("%m-%d-%Y-%H-%M-%S"),
        help="ID or suffix to append to logfile, If empty, date is appended",
    ),
    verbose: bool = typer.Option(
        False, "-v", help="Verbose logging. If True, sets loglevel to INFO"
    ),
    very_verbose: bool = typer.Option(
        False, "--vv", help="Very verbose logging. If True, sets loglevel to DEBUG"
    ),
    overwrite: bool = typer.Option(
        False,
        "-overwrite",
        help="If True, remove directories where prior results for session/participant may exist",
    ),
):

    """
    Export XNAT DICOM images in an experiment to a BIDS friendly format
    """

    bids_root_dir = os.path.expanduser(bids_root_dir)
    build_dir = os.getcwd()
    bidsmap = None

    # Parse bidsmap file
    if bidsmap_file is not "":
        with Path(bidsmap_file).open() as f:
            bidsmap = json.load(f)

    # Set up working directory
    if not os.access(bids_root_dir, os.R_OK):
        raise ValueError(f"BIDS Root directory must exist: {bids_root_dir}")

    # Set up session
    connection = requests.Session()
    connection.verify = False
    connection.auth = (user, password)

    project, subject = get_project_and_subject_id(connection, host, session)

    pi_prefix, study_prefix, subject_prefix, session_prefix = prepare_bids_prefixes(
        project, subject, session_suffix
    )

    # Set up logging
    logs_dir = f"{bids_root_dir}/{pi_prefix}/{study_prefix}/logs"

    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    setup_logging(
        _logger,
        f"{logs_dir}/export-{log_id}.log",
        verbose=verbose,
        very_verbose=very_verbose,
    )

    export_session_dir = prepare_export_output_path(
        bids_root_dir,
        pi_prefix,
        study_prefix,
        subject_prefix,
        session_prefix,
        overwrite,
    )

    # Export
    scans = get_scan_ids(connection, host, session)
    scans = filter_scans(scans, seqlist=includeseq, skiplist=skipseq)
    scans = bidsmap_scans(scans, bidsmap)

    assign_bids_name(
        connection, host, subject, session, scans, build_dir, export_session_dir,
    )

    # Close connection(I don't think this works)
    connection.delete(f"{host}/data/JSESSION")
    connection.close()

    return project, subject


@app.command()
def run_heudiconv(
    project: str,
    subject: str,
    session: str,
    bids_root_dir: str,
    session_suffix: str = "01",
    log_id: str = datetime.now().strftime("%m-%d-%Y-%H-%M-%S"),
    verbose: str = False,
    very_verbose: str = False,
    cleanup: str = False,
    overwrite: str = False,
):
    """
    Run Heudiconv
    """
    print("run Heudiconv")


@app.command()
def xnat2bids(
    user: str,
    password: str,
    session: str,
    bids_root_dir: str,
    host: str = "https://bnc.brown.edu/xnat",
    session_suffix: str = "01",
    bidsmap_file: str = "",
    includeseq: List[int] = typer.Option(
        [],
        "-i",
        "--includeseq",
        help="Include this sequence only, can specify multiple times",
    ),
    skipseq: List[int] = typer.Option(
        [], "-s", "--skipseq", help="Exclude this sequence, can specify multiple times",
    ),
    log_id: str = datetime.now().strftime("%m-%d-%Y-%H-%M-%S"),
    verbose: bool = False,
    very_verbose: bool = False,
    cleanup: bool = False,
    overwrite: bool = False,
):
    """
    Export DICOM images from an XNAT experiment to a BIDS compliant directory
    """

    project, subject = dicom_export(
        user,
        password,
        session,
        bids_root_dir,
        host=host,
        session_suffix=session_suffix,
        bidsmap_file=bidsmap_file,
        seqlist=includeseq,
        skiplist=skipseq,
        log_id=log_id,
        verbose=verbose,
        very_verbose=very_verbose,
        cleanup=cleanup,
        overwrite=overwrite,
    )
    # run_heudiconv(
    #     session,
    #     project,
    #     subject,
    #     bids_root_dir,
    #     session_suffix=session_suffix,
    #     log_id=log_id,
    #     verbose=verbose,
    #     very_verbose=very_verbose,
    #     overwrite=overwrite,
    # )


def main():
    app()
