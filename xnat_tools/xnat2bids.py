from datetime import datetime
from typing import List
from xnat_tools.dicom_export import dicom_export
from xnat_tools.run_heudiconv import run_heudiconv
import typer

app = typer.Typer()


@app.command()
def xnat2bids(
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
        "--overwrite",
        help="If True, remove directories where prior results for session/participant may exist",
    ),
    cleanup: bool = typer.Option(
        False,
        help="If True, Remove xnat-export folder and move logs to derivatives/xnat/logs inside bids directory",
    ),
):
    """
    Export DICOM images from an XNAT experiment to a BIDS compliant directory
    """

    project, subject = dicom_export(
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
        very_verbose=very_verbose,
        overwrite=overwrite,
    )

    r = run_heudiconv(
        project,
        subject,
        session,
        bids_root_dir,
        session_suffix=session_suffix,
        log_id=log_id,
        verbose=verbose,
        very_verbose=very_verbose,
        overwrite=overwrite,
        cleanup=cleanup,
    )
    return r


def main():
    app()
