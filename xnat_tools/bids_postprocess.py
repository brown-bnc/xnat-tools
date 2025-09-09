import logging
import os
from typing import List

import typer

from xnat_tools.bids_utils import (
    append_phase_units_field,
    insert_intended_for_fmap,
    path_string_preprocess,
    remove_func_acquisition_duration_field,
)
from xnat_tools.logging import setup_logging
from xnat_tools.xnat_utils import close_session, establish_connection, get_project_subject_session

_logger = logging.getLogger(__name__)

app = typer.Typer()


@app.command()
def bids_postprocess(
    bids_experiment_dir: str = typer.Argument(
        ..., help="Root output directory for exporting the files"
    ),
    user: str = typer.Option(None, "-u", "--user", prompt=True, help="XNAT User"),
    password: str = typer.Option(
        None, "-p", "--pass", prompt=True, hide_input=True, help="XNAT Password"
    ),
    host: str = typer.Option("https://xnat.bnc.brown.edu", "-h", "--host", help="XNAT's URL"),
    session: str = typer.Option(
        "", help="XNAT Session ID, that is the Accession # for an experiment."
    ),
    includesess: List[str] = typer.Option(
        [],
        "-n",
        "--includesess",
        help="Include this session only, this flag can be specified multiple time",
    ),
    includesubj: List[str] = typer.Option(
        [],
        "-i",
        "--includesubj",
        help="Include this participant only, this flag can be specified multiple times",
    ),
    skipsubj: List[str] = typer.Option(
        [],
        "-s",
        "--skipsubj",
        help="Skip this participant, this flag can be specified multiple times",
    ),
    skipsess: List[str] = typer.Option(
        [],
        "-k",
        "--skipsess",
        help="Skip this session, this flag can be specified multiple times",
    ),
    log_file: str = typer.Option(
        "",
        help="File to send logs to",
    ),
    verbose: int = typer.Option(
        0,
        "-v",
        "--verbose",
        count=True,
        help="Verbosity level. This flag can be specified multiple times to increase verbosity",
    ),
    overwrite: bool = typer.Option(
        False,
        "--overwrite",
        help="Inititate BIDS post-processing on all subjects located at the specified BIDS \
            directory, with intent to ovewrite existing data.",
    ),
):
    """
    Script for performing post BIDSIFY processing.
    At the moment it inserts the IntendedFor field
    to JSON sidecar for fieldmap data, and removes
    the AcquisitionDuration key from func jsons if
    RepetitionTime is present, because they are
    mutually exclusive according to BIDS spec
    """

    setup_logging(_logger, log_file, verbose_level=verbose)
    bids_experiment_dir = os.path.expanduser(bids_experiment_dir)

    # Set up working directory
    if not os.access(bids_experiment_dir, os.R_OK):
        raise ValueError("BIDS Experiment directory must exist")

    if session != "":
        # Set up session
        connection = establish_connection(user, password)

        project, subject, session_suffix = get_project_subject_session(
            connection, host, session, "-1"
        )

        close_session(connection, host)

        session_info = path_string_preprocess(project, subject, session_suffix)

        includesubj = [session_info[1]]

        session_suffix = session_info[2]

        insert_intended_for_fmap(bids_experiment_dir, includesubj, session_suffix, overwrite)
        remove_func_acquisition_duration_field(
            bids_experiment_dir,
            includesubj,
            session_suffix,
            includesess,
        )

        append_phase_units_field(
            bids_experiment_dir,
            includesubj,
            session_suffix,
            includesess,
        )

    else:
        if includesubj == []:
            files = os.listdir(bids_experiment_dir)
            includesubj = [x for x in files if x.startswith("sub-")]

        includesubj = [str(x).strip("sub-") for x in includesubj]

        skipsubj = [str(x).strip("sub-") for x in skipsubj]

        if skipsubj != []:
            includesubj = [x for x in includesubj if x not in skipsubj]

        if includesess == []:
            for subj in includesubj:
                subj_path = f"{bids_experiment_dir}/sub-{subj}"
                files = os.listdir(subj_path)
                includesess = [x for x in files if x.startswith("ses-")]

        includesess = [str(x).replace("ses-", "") for x in includesess]

        skipsess = [str(x).replace("ses-", "") for x in skipsess]

        if skipsess != []:
            _logger.info("---------------------------------")
            _logger.info(f"Skipping Sessions {skipsess}: ")
            _logger.info("---------------------------------")

            includesess = [x for x in includesess if x not in skipsess]

        _logger.info("---------------------------------")
        _logger.info(f"Processing Subjects {includesubj}: ")
        _logger.info("---------------------------------")

        _logger.info("---------------------------------")
        _logger.info(f"Processing Sessions {includesess}: ")
        _logger.info("---------------------------------")

        insert_intended_for_fmap(
            bids_experiment_dir,
            includesubj,
            session,
            includesess,
            overwrite,
        )

        remove_func_acquisition_duration_field(
            bids_experiment_dir,
            includesubj,
            session,
            includesess,
        )

        append_phase_units_field(
            bids_experiment_dir,
            includesubj,
            session,
            includesess,
        )


def main():
    """Entry point for console_scripts"""
    app()
