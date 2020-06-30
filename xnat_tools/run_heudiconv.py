import subprocess
import sys
import argparse
import shlex
import shutil
import glob
from datetime import datetime
from subprocess import Popen, PIPE, STDOUT
from pathlib import Path
from xnat_tools.xnat_utils import *
from xnat_tools.bids_utils import *


def parse_args(args):
    """Parse command line parameters

    Args:
      args ([str]): command line parameters as list of strings

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(
        description="Run Heudiconv on DICOMS form XNAT dump using Reproin Heuristic"
    )
    parser.add_argument("--host", default="https://bnc.brown.edu/xnat", help="Host")
    parser.add_argument("-u", "--user", help="XNAT username", required=True)
    parser.add_argument(
        "-p",
        "--password",
        type=XNATPass,
        help="XNAT password",
        default=XNATPass.DEFAULT,
    )
    parser.add_argument("--session", help="Session ID", required=True)
    parser.add_argument(
        "--session_suffix",
        help="Suffix of the session for BIDS e.g, 01. This will produce a sesstion label of sess-01",
        required=True,
        type=str,
    )
    parser.add_argument(
        "--bids_root_dir", help="Root output directory for BIDS files", required=True
    )
    parser.add_argument(
        "--cleanup",
        help="Remove/mode files and folders outside the bids directory",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--log_id",
        help="ID or suffix to append to logfile, If empty, date is appended",
        required=False,
        default=datetime.now().strftime("%m-%d-%Y-%H-%M-%S"),
        type=str
    )
    parser.add_argument(
        "--overwrite",
        help="Remove directories where prior results for session/participant may exist",
        action='store_true',
        default=False)

    args, _ = parser.parse_known_args(args)
    return args


def main(args):
    """Main entry point allowing external calls

    Args:
      args ([str]): command line parameter list
    """

    host = args.host
    session = args.session
    session_suffix = args.session_suffix
    bids_root_dir = os.path.expanduser(args.bids_root_dir)
    build_dir = os.getcwd()
    cleanup = args.cleanup
    log_id = args.log_id
    overwrite = args.overwrite

    # Set up working directory
    if not os.access(bids_root_dir, os.R_OK):
        raise ValueError("BIDS Root directory must exist")

    # Set up session
    connection = requests.Session()
    connection.verify = False
    connection.auth = (args.user, args.password)

    project, subject = get_project_and_subject_id(connection, host, session)
    connection.delete(f"{host}/data/JSESSION")
    connection.close()

    # get PI from project name
    investigator = project.lower().split("_")[0]

    # Paths to export source data in a BIDS friendly way
    pi_prefix, study_prefix, subject_prefix, session_prefix = prepare_heudi_prefixes(
        project, subject, session_suffix
    )
    heudi_output_dir = prepare_heudiconv_output_path(
        bids_root_dir, pi_prefix, study_prefix, subject_prefix, session_prefix
    )
    dicom_dir_template = f"{bids_root_dir}/{pi_prefix}/{study_prefix}/xnat-export/sub-{subject}/ses-{session_prefix}"

    # check if the extension of the images is dcm or IMA
    dicom_ext = "dcm"
    if len(glob.glob(f"{dicom_dir_template}/*/*.dcm")) == 0:
        if len(glob.glob(f"{dicom_dir_template}/*/*.IMA")) > 0:
            dicom_ext = "IMA"
        else:
            raise ValueError(f"No .dcm or .IMA files found in {dicom_dir_template}")

    heudi_cmd = f"heudiconv -f reproin --bids \
    -o {heudi_output_dir} \
    --dicom_dir_template {bids_root_dir}/{pi_prefix}/{study_prefix}/xnat-export/sub-{{subject}}/ses-{{session}}/*/*.{dicom_ext} \
    --subjects {subject_prefix} --ses {session_prefix}"

    heudi_split_cmd = shlex.split(heudi_cmd)

    print(f"Executing Heudiconv command: {heudi_cmd}")


    logfile = str(Path(heudi_output_dir).parent) + f"/logs/heudiconv-{log_id}.log"


    with Popen(heudi_split_cmd, stdout=PIPE, stderr=STDOUT, bufsize=1, universal_newlines=True) as p: 
        with open(logfile, 'a') as file: 
            for line in p.stdout: 
                sys.stdout.write(line) 
                file.write(line) 

    print("Done with Heudiconv BIDS Convesion.")

    if cleanup:
        print("Removing XNAT export.")
        shutil.rmtree(f"{bids_root_dir}/{pi_prefix}/{study_prefix}/xnat-export")

        print("Moving XNAT export log to derivatives folder")

        # check if directory exists or not yet
        derivatives_dir = (
            f"{bids_root_dir}/{pi_prefix}/{study_prefix}/bids/derivatives/xnat/logs"
        )
        if not os.path.exists(derivatives_dir):
            os.mkdir(derivatives_dir)


def run():
    """Entry point for console_scripts
    """
    args = parse_args(sys.argv[1:])
    main(args)


if __name__ == "__main__":
    run()
