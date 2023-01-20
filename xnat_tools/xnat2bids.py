import glob
from datetime import datetime
from typing import List

import typer

from xnat_tools.bids_postprocess import bids_postprocess
from xnat_tools.dicom_export import dicom_export
from xnat_tools.run_heudiconv import run_heudiconv

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
    includeseq: List[int] = typer.Option(
        [],
        "-i",
        "--includeseq",
        help="Include this sequence only, this flag can specify multiple times",
    ),
    skipseq: List[int] = typer.Option(
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
        help="Remove xnat-export folder and move logs to derivatives/xnat/logs",
    ),
):
    """
    Export DICOM images from an XNAT experiment to a BIDS compliant directory
    """

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
    )

    r = run_heudiconv(
        project,
        subject,
        bids_root_dir,
        session_suffix=session_suffix,
        log_id=log_id,
        overwrite=overwrite,
        cleanup=cleanup,
    )

    bids_experiment_dir = glob.glob(f"{bids_root_dir}/*/*/bids")[0]

    bids_postprocess(
        bids_experiment_dir,
        user=user,
        password=password,
        session="",
        includesess=[],
        includesubj=[],
        skipsubj=[],
        log_file="",
        verbose=0,
        overwrite=False,
    )

    return r


def main():
    app()
