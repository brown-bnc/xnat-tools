


import subprocess
import sys
import argparse
import shlex
import shutil
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
        description="Run Heudiconv on DICOMS form XNAT dump using Reproin Heuristic")
    parser.add_argument(
        "--host",
        default="https://bnc.brown.edu/xnat",
        help="Host")
    parser.add_argument(
        "-u", "--user",
        help="XNAT username",
        required=True)
    parser.add_argument(
        '-p', '--password',
        type=XNATPass,
        help='XNAT password',
        default=XNATPass.DEFAULT)
    parser.add_argument(
        "--session",
        help="Session ID",
        required=True)
    parser.add_argument(
        "--bids_root_dir",
        help="Root output directory for BIDS files",
        required=True)
    parser.add_argument(
        "--cleanup",
        help="Remove/mode files and folders outside the bids directory",
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
    bids_root_dir = os.path.expanduser(args.bids_root_dir)
    build_dir = os.getcwd()
    cleanup = args.cleanup

    # Set up working directory
    if not os.access(bids_root_dir, os.R_OK):
        raise ValueError('BIDS Root directory must exist')

    # Set up session
    connection = requests.Session()
    connection.verify = False
    connection.auth = (args.user, args.password)
    
    project, subject = get_project_and_subject_id(connection, host, session)
    connection.delete(f"{host}/data/JSESSION")
    connection.close()

    #get PI from project name
    investigator = project.lower().split('_')[0] 

    # Paths to export source data in a BIDS friendly way
    pi_prefix, study_prefix, subject_prefix, session_prefix = prepare_heudi_prefixes(project, subject, session)

    heudi_output_dir = prepare_heudiconv_output_path(bids_root_dir, pi_prefix, study_prefix, subject_prefix, session_prefix)

    heudi_cmd = f"heudiconv -f reproin --bids \
    -o {heudi_output_dir} \
    --dicom_dir_template {bids_root_dir}/{pi_prefix}/{study_prefix}/xnat-export/sub-{{subject}}/ses-{{session}}/*/*.dcm \
    --subjects {subject_prefix} --ses {session_prefix}"

    heudi_split_cmd = shlex.split(heudi_cmd)
    
    print(f"Executing Heudiconv command: {heudi_cmd}")

    stdout_file = open(str(Path(heudi_output_dir).parent) + "/logs/heudiconv_stdout.log", 'a')
    stderr_file = open(str(Path(heudi_output_dir).parent) + "/logs/heudiconv_stderr.log", 'a') 
    
    process = subprocess.run(heudi_split_cmd, 
                        stdout = stdout_file,
                        stderr = stderr_file,
                        universal_newlines = True)
    # process = subprocess.run(heudi_split_cmd)

    stdout_file.close()
    stderr_file.close()
    print("Done with Heudiconv BIDS Convesion.")

    if cleanup:
        print("Removing XNAT export.")
        # shutil.rmtree(f"{bids_root_dir}/{pi_prefix}/{study_prefix}/xnat-export")
        print("Moving XNAT export log to derivatives folder")

        # check if directory exists or not yet
        derivatives_dir = f"{bids_root_dir}/{pi_prefix}/{study_prefix}/bids/derivatives/xnat/logs"
        if not os.path.exists(derivatives_dir):
            os.mkdir(derivatives_dir)



def run():
    """Entry point for console_scripts
    """
    args = parse_args(sys.argv[1:])
    main(args)


if __name__ == "__main__":
    run()