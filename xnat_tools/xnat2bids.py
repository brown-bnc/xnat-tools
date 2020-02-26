import sys
import argparse
import xnat_tools.dicom_export as dicom_export
import xnat_tools.run_heudiconv as run_heudiconv


def parse_args(args):
    """Parse command line parameters

    Args:
      args ([str]): command line parameters as list of strings

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(
        description="BIDSify an XNAT session")
    parser.add_argument(
        "--host",
        default="http://bnc.brown.edu/xnat",
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
        "--bidsmap_file",
        help="Bidsmap JSON file to correct sequence names",
        required=False,
        default="")
    parser.add_argument(
        "--seqlist",
        help="List of sequences from XNAT to run if don't want to process all seuqences",
        required=False,
        default=[],
        nargs="*",  # 0 or more values expected => creates a list
        type=int)
    parser.add_argument(
        '-v',
        '--verbose',
        dest="loglevel",
        help="set loglevel to INFO",
        action='store_const',
        const=logging.INFO)
    parser.add_argument(
        '-vv',
        '--very-verbose',
        dest="loglevel",
        help="set loglevel to DEBUG",
        action='store_const',
        const=logging.DEBUG)
    parser.add_argument(
        "--cleanup",
        help="Remove/mode files and folders outside the bids directory",
        action='store_true',
        default=False)
    return parser.parse_args(args)



def run():
    """Entry point for console_scripts
    """
    args = dicom_export.parse_args(sys.argv[1:])
    dicom_export.main(args)
    args = run_heudiconv.parse_args(sys.argv[1:])
    run_heudiconv.main(args)

if __name__ == "__main__":
    run()