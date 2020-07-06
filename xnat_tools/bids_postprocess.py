import subprocess
import sys
import argparse
import coloredlogs, logging
import shlex
import shutil
from pathlib import Path
from xnat_tools.bids_utils import *

_logger = logging.getLogger(__name__)


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
    parser.add_argument(
        "--session_suffix",
        help="Suffix of the session for BIDS e.g, 01. This will produce a sesstion label of sess-01",
        required=True,
        type=str,
    )
    parser.add_argument(
        "--bids_experiment_dir",
        help="Root for BIDS for current experiment. The sub-* subfolders are expected under this directory",
        required=True,
    )
    parser.add_argument(
        "--subjlist",
        help="List of participants to post process. If empty, all participants are processed. Accepts a list --subjlist 1 2 3",
        required=False,
        default=[],
        nargs="*",  # 0 or more values expected => creates a list
        type=str,
    )
    parser.add_argument(
        "--skipsubj",
        help="List of participants to SKIP. Accepts a list --skipsubj 1 2 3",
        required=False,
        default=[],
        nargs="*",  # 0 or more values expected => creates a list
        type=str,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        help="set loglevel to INFO",
        action="store_const",
        const=logging.INFO,
    )
    parser.add_argument(
        "-vv",
        "--very-verbose",
        dest="loglevel",
        help="set loglevel to DEBUG",
        action="store_const",
        const=logging.DEBUG,
    )

    args, _ = parser.parse_known_args(args)
    return args


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    if loglevel is None:
        loglevel = logging.INFO

    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel,
        format=logformat,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    coloredlogs.install(level=loglevel, logger=_logger)


def main(args):
    """Main entry point allowing external calls

    Args:
      args ([str]): command line parameter list
    """
    setup_logging(args.loglevel)

    bids_experiment_dir = os.path.expanduser(args.bids_experiment_dir)
    subjlist = args.subjlist
    skipsubj = args.skipsubj

    # Set up working directory
    if not os.access(bids_experiment_dir, os.R_OK):
        raise ValueError("BIDS Experiment directory must exist")

    if subjlist == []:
        files = os.listdir(bids_experiment_dir)
        subjlist = [x for x in files if x.startswith("sub-")]

    subjlist = [x.strip("sub-") for x in subjlist]
    skipsubj = [x.strip("sub-") for x in skipsubj]

    if skipsubj != []:
        subjlist = [x for x in subjlist if x not in skipsubj]

    _logger.info("---------------------------------")
    _logger.info(f"Processing Subjects {subjlist}: ")
    _logger.info("---------------------------------")

    insert_intended_for_fmap(bids_experiment_dir, subjlist)


def run():
    """Entry point for console_scripts
    """
    args = parse_args(sys.argv[1:])
    main(args)


if __name__ == "__main__":
    run()
