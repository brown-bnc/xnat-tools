import logging
import sys

import coloredlogs

if not sys.warnoptions:
    import warnings

    warnings.simplefilter("once")


def setup_logging(logger, logfile: str = "", verbose_level: int = 0, very_verbose: bool = False):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """

    loglevel = logging.INFO
    if verbose_level >= 1:
        loglevel = logging.DEBUG
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    handlers = [logging.StreamHandler(sys.stdout)]
    if logfile:
        handlers.append(logging.FileHandler(logfile))

    logging.basicConfig(
        level=loglevel,
        format=logformat,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
    )
    logging.captureWarnings(True)
    coloredlogs.install(level=loglevel, logger=logger)
