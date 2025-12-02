import glob
import os
import re
import shlex
import shutil
import sys
from datetime import datetime
from pathlib import Path
from subprocess import PIPE, Popen

import typer
from heudiconv.dicoms import compress_dicoms
from heudiconv.utils import TempDirs

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
    dicom_dir = Path(export_dir) / subject_prefix / session_prefix

    # check if the extension of the images is dcm or IMA
    if (len(glob.glob(f"{dicom_dir}/*/*.dcm")) == 0) and len(
        glob.glob(f"{dicom_dir}/*/*.IMA")
    ) == 0:
        raise ValueError(f"No .dcm or .IMA files found in {dicom_dir}")

    # all first-level series directories under the session
    series_dirs = [d for d in dicom_dir.iterdir() if d.is_dir()]

    # filter specific scan types / scanner derivatives that we know will break heudiconv
    # some of these we will handle ourselves afterward
    heudi_skip_list = [
        "_MPR_",
        "_ND",
        "rf_map",
        "tb1tfl",
        "TB1TFL",
        "_TRACEW",
        "_TENSOR",
        "_B0",
        "_ColFA",
        "_ADC",
    ]

    # split off bottom 3 levels because they need to be supplied as a locator path
    heudi_base_dir = Path(heudi_output_dir).parents[3]
    heudi_locator = Path(heudi_output_dir).relative_to(heudi_base_dir)

    keep_dirs, skip_dirs = [], []

    for d in series_dirs:
        if any(s in d.name for s in heudi_skip_list):
            skip_dirs.append(d)
        else:
            keep_dirs.append(d)

    if skip_dirs:
        print(f"Skipping heudiconv BIDS conversion for {', '.join(s.name for s in skip_dirs)}")
        print(f"DICOMS for those scans can be found in {str(heudi_output_dir)}/sourcedata")

    if not keep_dirs:
        raise RuntimeError(
            f"No DICOM directories left after filtering XNAT export directory {dicom_dir}"
        )

    # Build heudiconv command using --files option, which will still look within directories
    heudi_cmd = [
        "heudiconv",
        "-f",
        "reproin",
        "--bids",
        "-o",
        str(heudi_base_dir),
        "--files",
        *[str(d) for d in keep_dirs],
        "--locator",
        str(heudi_locator),
        "--subjects",
        subject,
        "--ses",
        session_suffix,
    ]

    if overwrite:
        heudi_cmd.append("--overwrite")

    print("Executing Heudiconv command:", " ".join(shlex.quote(a) for a in heudi_cmd))

    logdir = str(Path(heudi_output_dir).parent) + "/logs"
    logfile = f"{logdir}/heudiconv-{log_id}.log"

    with Popen(heudi_cmd, stdout=PIPE, stderr=PIPE, bufsize=1, universal_newlines=True) as p, open(
        logfile, "a", encoding="utf-8"
    ) as file:
        stdout, stderr = p.communicate()
        sys.stdout.write(stdout)
        file.write(stdout)
        file.write(stderr)

        if p.returncode != 0:
            raise RuntimeError(f"Heudiconv failed with exit code {p.returncode}:\n{stderr}")

    # copy over any skipped DICOMs into the bids/sourcedata/subject/session directory
    tempdirs = TempDirs()
    sourcedata_dir = f"{heudi_output_dir}/sourcedata/sub-{subject}/ses-{session_suffix}/"
    bids_datatypes = ["anat", "func", "dwi", "fmap", "perf", "mrs"]

    for s in skip_dirs:
        dirname = re.split("-|_", s.name)[0]
        if dirname in bids_datatypes:
            pass
        else:
            dirname = "unknown"
        if not Path(sourcedata_dir, dirname).exists():
            os.makedirs(str(Path(sourcedata_dir, dirname)))
        compress_dicoms(
            glob.glob(f"{str(s)}/*"), f"{sourcedata_dir}{dirname}/{s.name}", tempdirs, False
        )

    print("Done with Heudiconv BIDS conversion.")

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
