import sys
import argparse
import dicom_export
import run_heudiconv


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



def run():
    """Entry point for console_scripts
    """
    dicom_export.main(sys.argv[1:])
    run_heudiconv.main(sys.argv[1:])


if __name__ == "__main__":
    run()