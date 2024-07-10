from datetime import datetime
from typing import List

import typer

from xnat_tools.bids_utils import path_string_preprocess
from xnat_tools.dcm2bids import dcm2bids
from xnat_tools.dicom_export import dicom_export
from xnat_tools.physio_convert import physio_convert
from xnat_tools.xnat_utils import establish_connection, get_project_subject_session

app = typer.Typer()


@app.command()
def xnat2bids(
    session: str = typer.Argument(
        ..., help="XNAT Session ID, that is the Accession # for an experiment."
    ),
    bids_root_dir: str = typer.Argument(..., help="Root output directory for exporting the files"),
    user: str = typer.Option(None, "-u", "--user", prompt=True, help="XNAT User"),
    password: str = typer.Option(
        None, "-p", "--pass", prompt=True, hide_input=True, help="XNAT Password"
    ),
    host: str = typer.Option("https://xnat.bnc.brown.edu", "-h", "--host", help="XNAT'sURL"),
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
        help="Exclude this sequence, can be specified multiple times",
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
        help="Verbose level. This flag can be specified multiple times to increase verbosity",
    ),
    overwrite: bool = typer.Option(
        False,
        "--overwrite",
        help="Remove directories where prior results for this session/participant",
    ),
    cleanup: bool = typer.Option(
        False,
        "--cleanup",
        help="Remove xnat-export folder and move logs to derivatives/xnat/logs",
    ),
    skip_export: bool = typer.Option(
        False,
        "--skip-export",
        help="Skip DICOM Export, while only running BIDS conversion",
    ),
    export_only: bool = typer.Option(
        False,
        "--export-only",
        help="Run DICOM Export without subsequent BIDS conversion",
    ),
    validate_frames: bool = typer.Option(
        False,
        "--validate_frames",
        help=(
            "Validate the frame counts of all acquisitions of functional bold sequences. "
            "If the final acquisition does not contain the expected number of slices, "
            "the associated DICOM file will be deleted."
        ),
    ),
    correct_dicoms_config: str = typer.Option(
        "", "-d", "--dicomfix-config", help="JSON file to correct DICOM fields. USE WITH CAUTION"
    ),
):
    """
    Export DICOM images from an XNAT experiment to a BIDS compliant directory
    """

    if not skip_export:

        project, subject, session_suffix = dicom_export(
            session,
            bids_root_dir,
            user=user,
            password=password,
            host=host,
            session_suffix=session_suffix,
            bidsmap_file=bidsmap_file,
            includeseq=includeseq,
            skipseq=skipseq,
            log_id=log_id,
            verbose=verbose,
            overwrite=overwrite,
            validate_frames=validate_frames,
            correct_dicoms_config=correct_dicoms_config,
        )

    if not export_only:

        if "project" not in locals():
            conn = establish_connection(user, password)
            project, subject, session_suffix = get_project_subject_session(
                conn, host, session, session_suffix
            )
            project, subject, session_suffix = path_string_preprocess(
                project, subject, session_suffix
            )

        r = dcm2bids(
            project,
            subject,
            bids_root_dir,
            session,
            user=user,
            password=password,
            session_suffix=session_suffix,
            log_id=log_id,
            overwrite=overwrite,
            cleanup=cleanup,
        )

        physio_convert(project, subject, bids_root_dir, session_suffix)

    return True if export_only else r


def main():
    app()
