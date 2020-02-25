


import subprocess
import sys
import argparse
import shlex
from os import walk
from pathlib import Path
from xnat_tools.xnat_utils import *
from xnat_tools.bids_utils import *
from bids_validator import BIDSValidator


def parse_args(args):
    """Parse command line parameters

    Args:
      args ([str]): command line parameters as list of strings

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(
        description="Dump DICOMS to a BIDS firendly sourcedata directory")
    parser.add_argument(
        "--host",
        default="",
        help="Host",
        required=True)
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

    return parser.parse_args(args)

def validate(heudi_output_dir):
    bids_result = BIDSValidator().is_bids(heudi_output_dir)
    return bids_result

def main(args):
    """Main entry point allowing external calls

    Args:
      args ([str]): command line parameter list
    """
    args = parse_args(args)

    host = args.host
    session = args.session
    bids_root_dir = os.path.expanduser(args.bids_root_dir)
    build_dir = os.getcwd()

    # Set up working directory
    if not os.access(bids_root_dir, os.R_OK):
        raise ValueError('BIDS Root directory must exist')

    # Set up session
    connection = requests.Session()
    connection.verify = False
    connection.auth = (args.user, args.password)
    
    project, subject = get_project_and_subject_id(connection, host, session)
    connection.close()

    #get PI from project name
    investigator = project.lower().split('_')[0] 

    # Paths to export source data in a BIDS friendly way
    pi_prefix, study_prefix, subject_prefix, session_prefix = prepare_heudi_prefixes(project, subject, session)

    heudi_output_dir = prepare_heudiconv_output_path(bids_root_dir, pi_prefix, study_prefix, subject_prefix, session_prefix)


    # from os import walk
    # f = []
    print("---------------------------------------------------")
    print(f"Validating BIDS for directory {heudi_output_dir}.")

    path = heudi_output_dir + "/sub-" + subject_prefix + "/ses-" +session_prefix
    for (dirpath, dirnames, filenames) in walk(path):
        for file in filenames:
            bids_file = os.path.join(dirpath, file)
            valid = validate(bids_file)
            print(f"{valid}: {file}")


    # break
    

    print(path)

    print("Done Validating BIDS.")
    print("---------------------------------------------------")



def run():
    """Entry point for console_scripts
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    run()