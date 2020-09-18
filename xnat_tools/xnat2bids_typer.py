import sys
import logging
import typer
from datetime import datetime
from typing import List

# from xnat_tools.xnat_utils import XNATPass

app = typer.Typer()


@app.command()
def dicom_export(
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
    Export XNAT DICOM images in an experiment to a BIDS friendly format
    """
    print(f"run dicom export")


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

    print(includeseq)
    # project, subject = dicom_export(
    #     user,
    #     password,
    #     session,
    #     bids_root_dir,
    #     host=host,
    #     session_suffix=session_suffix,
    #     bidsmap_file=bidsmap_file,
    #     seqlist=seqlist,
    #     skiplist=skiplist,
    #     log_id=log_id,
    #     verbose=verbose,
    #     very_verbose=very_verbose,
    #     cleanup=cleanup,
    #     overwrite=overwrite,
    # )
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


if __name__ == "__main__":
    app()
