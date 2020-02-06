


import subprocess
import sys
import argparse
import shlex
from xnat_utils import *
from bids_utils import *


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
        default="http://bnc.brown.edu/xnat-dev",
        help="DEV host",
        required=True)
    parser.add_argument(
        "--user",
        help="CNDA username",
        required=True)
    parser.add_argument(
        "--password",
        help="Password",
        required=True)
    parser.add_argument(
        "--session",
        help="Session ID",
        required=True)
    parser.add_argument(
        "--subject",
        help="Subject Label",
        required=False)
    parser.add_argument(
        "--project",
        help="Project",
        required=False)
    parser.add_argument(
        "--bids_root_dir",
        help="Root output directory for BIDS files",
        required=True)
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1')

    return parser.parse_args(args)

  

def main(args):
    """Main entry point allowing external calls

    Args:
      args ([str]): command line parameter list
    """
    args = parse_args(args)

    host = args.host
    session = args.session
    subject = args.subject
    project = args.project
    bids_root_dir = args.bids_root_dir
    build_dir = os.getcwd()

    # Set up working directory
    if not os.access(bids_root_dir, os.R_OK):
        raise ValueError('BIDS Root directory must exist')

    # Set up session
    connection = requests.Session()
    connection.verify = False
    connection.auth = (args.user, args.password)
    
    if project is None or subject is None:
        project, subject = get_project_and_subject_id(connection, host, project, subject, session)

    #get PI from project name
    investigator = project.lower().split('_')[0] 

    # Paths to export source data in a BIDS friendly way
    pi_prefix, study_prefix, subject_prefix, session_prefix = prepare_heudi_prefixes(project, subject, session)

    heudi_output_dir = prepare_heudiconv_output_path(bids_root_dir, pi_prefix, study_prefix, subject_prefix, session_prefix)
    

    stdout_file = open(heudi_output_dir + "/heudiconv_stdout.log", 'a')
    stderr_file = open(heudi_output_dir + "/heudiconv_stderr.log", 'a') 

    heudi_cmd = f"heudiconv -f reproin --bids \
    -o {heudi_output_dir} \
    --dicom_dir_template /data/xnat/bids-export/{pi_prefix}/{study_prefix}/xnat-export/sub-{{subject}}/ses-{{session}}/*/*.dcm \
    --subjects {subject_prefix} --ses {session_prefix}"

    heudi_split_cmd = shlex.split( heudi_cmd)
    
    print(f"Starting Heudiconv BIDS Convesion. STDOUT AND STDERR live under {heudi_output_dir}/heudiconv_stdout/err.log")
    print(f"Executing Heudiconv command: {heudi_cmd}")
    process = subprocess.run(heudi_split_cmd, 
                        stdout = stdout_file,
                        stderr = stderr_file,
                        universal_newlines = True)

    print("Done with Heudiconv BIDS Convesion.")

    stdout_file.close()
    stderr_file.close()


def run():
    """Entry point for console_scripts
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    run()