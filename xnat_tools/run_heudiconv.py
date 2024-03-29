import glob
import os
import shlex
import shutil
import sys
from datetime import datetime
from pathlib import Path
from subprocess import PIPE, STDOUT, Popen

import typer

from xnat_tools.bids_utils import (
    path_string_preprocess,
    prepare_heudiconv_output_path,
    prepare_path_prefixes,
)

app = typer.Typer()


@app.command()
def run_heudiconv(
    project: str = typer.Argument(..., help="XNAT's Project ID"),
    subject: str = typer.Argument(..., help="XNAT's subject ID"),
    bids_root_dir: str = typer.Argument(..., help="Root output directory for exporting files"),
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
    """
    Run Heudiconv
    """
    print("************************")
    bids_root_dir = os.path.expanduser(bids_root_dir)

    # Set up working directory
    if not os.access(bids_root_dir, os.R_OK):
        raise ValueError("BIDS Root directory must exist")

    # Paths to export source data in a BIDS friendly way
    project, subject, session_suffix = path_string_preprocess(project, subject, session_suffix)

    pi_prefix, study_prefix, subject_prefix, session_prefix = prepare_path_prefixes(
        project, subject, session_suffix
    )

    heudi_output_dir = prepare_heudiconv_output_path(
        bids_root_dir,
        pi_prefix,
        study_prefix,
        subject_prefix,
        session_prefix,
        overwrite,
    )

    export_dir = f"{bids_root_dir}/{pi_prefix}/{study_prefix}/xnat-export"
    dicom_dir_template = f"{export_dir}/{subject_prefix}/{session_prefix}"

    # check if the extension of the images is dcm or IMA
    dicom_ext = "dcm"
    if len(glob.glob(f"{dicom_dir_template}/*/*.dcm")) == 0:
        if len(glob.glob(f"{dicom_dir_template}/*/*.IMA")) > 0:
            dicom_ext = "IMA"
        else:
            raise ValueError(f"No .dcm or .IMA files found in {dicom_dir_template}")

    heudi_cmd = f"heudiconv -f reproin --bids \
    -o {heudi_output_dir} \
    --dicom_dir_template {export_dir}/sub-{{subject}}/ses-{{session}}/*/*.{dicom_ext} \
    --subjects {subject} --ses {session_suffix}"

    if overwrite:
        heudi_cmd = heudi_cmd + " --overwrite"

    heudi_split_cmd = shlex.split(heudi_cmd)

    print(f"Executing Heudiconv command: {heudi_cmd}")

    logfile = str(Path(heudi_output_dir).parent) + f"/logs/heudiconv-{log_id}.log"

    with Popen(
        heudi_split_cmd, stdout=PIPE, stderr=STDOUT, bufsize=1, universal_newlines=True
    ) as p:
        with open(logfile, "a") as file:
            ouput, _ = p.communicate()
            for line in ouput:
                sys.stdout.write(line)
                file.write(line)
        if p.returncode != 0:
            raise RuntimeError("Heudiconv was asked to overwrite files. Try the --overwite flag")

    print("Done with Heudiconv BIDS Convesion.")

    if cleanup:
        print("Removing XNAT export.")
        shutil.rmtree(f"{bids_root_dir}/{pi_prefix}/{study_prefix}/xnat-export")

        print("Moving XNAT export log to derivatives folder")

        # check if directory exists or not yet
        derivatives_dir = f"{bids_root_dir}/{pi_prefix}/{study_prefix}/bids/derivatives/xnat/logs"
        if not os.path.exists(derivatives_dir):
            os.mkdir(derivatives_dir)

    return 0


def main():
    app()
