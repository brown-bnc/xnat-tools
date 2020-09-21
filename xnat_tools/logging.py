import coloredlogs
import logging
import sys


def setup_logging(
    logger, logfile: str, verbose: bool = False, very_verbose: bool = False
):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """

    loglevel = logging.INFO
    if very_verbose:
        loglevel = logging.DEBUG
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel,
        format=logformat,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.FileHandler(logfile), logging.StreamHandler(sys.stdout)],
    )
    coloredlogs.install(level=loglevel, logger=logger)
