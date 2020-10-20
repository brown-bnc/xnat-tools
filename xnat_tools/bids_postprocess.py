import logging
import os
from typing import List

import typer

from xnat_tools.bids_utils import insert_intended_for_fmap
from xnat_tools.logging import setup_logging

_logger = logging.getLogger(__name__)

app = typer.Typer()


@app.command()
def bids_postprocess(
    session: str = typer.Argument(
        ..., help="XNAT Session ID, that is the Accession # for an experiment."
    ),
    bids_experiment_dir: str = typer.Argument(
        ..., help="Root output directory for exporting the files"
    ),
    session_suffix: str = typer.Option(
        "01",
        "-ss",
        "--session-suffix",
        help="Suffix of the session for BIDS defaults to 01. \
        This will produce a session label of sess-01. \
        You likely only need to change the default for multi-session studies",
    ),
    includesubj: List[str] = typer.Option(
        [],
        "-i",
        "--includeseq",
        help="Include this participant only, can be specified multiple times",
    ),
    skipsubj: List[str] = typer.Option(
        [],
        "-s",
        "--skipseq",
        help="Skip this participant, can be specified multiple times",
    ),
    log_file: str = typer.Option(
        "",
        help="File to senf logs to",
    ),
    verbose: bool = typer.Option(
        False, "-v", help="Verbose logging. If True, sets loglevel to INFO"
    ),
    very_verbose: bool = typer.Option(
        False, "--vv", help="Very verbose logging. If True, sets loglevel to DEBUG"
    ),
):
    """
    Script for performing post BIDSIFY processing.
    At the moment it inserts the IntendedFor field
    to JSON sidecart for fieldmap data
    """

    setup_logging(
        _logger,
        log_file,
        verbose=verbose,
        very_verbose=very_verbose,
    )

    bids_experiment_dir = os.path.expanduser(bids_experiment_dir)

    # Set up working directory
    if not os.access(bids_experiment_dir, os.R_OK):
        raise ValueError("BIDS Experiment directory must exist")

    if includesubj == []:
        files = os.listdir(bids_experiment_dir)
        includesubj = [x for x in files if x.startswith("sub-")]

    includesubj = [str(x).strip("sub-") for x in includesubj]

    skipsubj = [str(x).strip("sub-") for x in skipsubj]

    if skipsubj != []:
        includesubj = [x for x in includesubj if x not in skipsubj]

    _logger.info("---------------------------------")
    _logger.info(f"Processing Subjects {includesubj}: ")
    _logger.info("---------------------------------")

    insert_intended_for_fmap(bids_experiment_dir, includesubj)


def main():
    """Entry point for console_scripts"""
    app()
