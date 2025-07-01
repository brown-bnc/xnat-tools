import glob
import os
from datetime import datetime

import typer

from xnat_tools.bids_postprocess import bids_postprocess
from xnat_tools.bids_utils import convert_mrs, prepare_path_prefixes, run_mne_eeg2bids
from xnat_tools.run_heudiconv import run_heudiconv

app = typer.Typer()


@app.command()
def dcm2bids(
    project: str = typer.Argument(..., help="XNAT's Project ID"),
    subject: str = typer.Argument(..., help="XNAT's subject ID"),
    bids_root_dir: str = typer.Argument(..., help="Root output directory for exporting files"),
    session: str = typer.Argument(
        ..., help="XNAT Session ID, that is the Accession # for an experiment."
    ),
    user: str = typer.Option(None, "-u", "--user", prompt=True, help="XNAT User"),
    password: str = typer.Option(
        None, "-p", "--pass", prompt=True, hide_input=True, help="XNAT Password"
    ),
    session_suffix: str = typer.Option(
        "-1",
        "-S",
        "--session-suffix",
        help="The session_suffix is initially set to -1.\
              This will signify an unspecified session_suffix and default to sess-01.\
              For multi-session studies, the session label will be pulled from XNAT",
    ),
    log_id: str = typer.Option(
        datetime.now().strftime("%m-%d-%Y-%H-%M-%S"),
        help="ID or suffix to append to logfile. If empty, current date is used",
    ),
    overwrite: bool = typer.Option(
        False,
        help="Remove directories where prior results for session/participant may exist",
    ),
    cleanup: bool = typer.Option(
        False,
        help="Remove xnat-export folder and move logs to derivatives/xnat/logs",
    ),
):

    pi_prefix, study_prefix, subject_prefix, session_prefix = prepare_path_prefixes(
        project, subject, session
    )

    bids_experiment_dir = f"{bids_root_dir}/{pi_prefix}/{study_prefix}/bids"

    # Build path to exported data
    xnat_data_path = (
        f"{bids_root_dir}/{pi_prefix}/{study_prefix}/xnat-export/"
        f"{subject_prefix}/ses-{session_suffix}/"
    )

    # Build path to exported eeg data
    eeg_data_path = f"{xnat_data_path}/eeg/"
    eeg_data = os.path.isdir(eeg_data_path)

    if len(glob.glob(xnat_data_path + "/*/*.dcm")) == 0:
        # if we have no DICOMs, allow it as long as there is an eeg directory
        if eeg_data:
            r = True
        else:
            raise RuntimeError("No DICOM files found to convert to BIDS format")
    else:
        r = run_heudiconv(
            project,
            subject,
            bids_root_dir,
            session_suffix=session_suffix,
            log_id=log_id,
            overwrite=overwrite,
            cleanup=cleanup,
        )

    # Convert EEG data to BIDS if present
    if eeg_data:
        run_mne_eeg2bids(
            subject,
            session_suffix,
            bids_experiment_dir,
            eeg_data_path,
        )

    for mrsdir in glob.glob(xnat_data_path + "/mrs-*"):
        convert_mrs(
            subject,
            session_suffix,
            bids_experiment_dir,
            mrsdir,
        )

    bids_postprocess(
        bids_experiment_dir,
        user=user,
        password=password,
        session=session,
        includesess=[session_suffix],
        includesubj=[subject],
        skipsubj=[],
        skipsess=[],
        log_file="",
        verbose=0,
        overwrite=False,
    )

    return r
