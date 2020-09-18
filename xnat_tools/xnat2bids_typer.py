import sys
import logging
import typer
from datetime import datetime
from typing import List, Path, Optional

# from xnat_tools.xnat_utils import XNATPass

app = typer.Typer()


@app.command()
def dicom_export(
    user: str,
    password: str,
    session: str,
    bids_root_dir: str,
    host: str = "https://bnc.brown.edu/xnat",
    session_suffix: str = "01",
    bidsmap_file: Optional[Path] = "",
    includeseq: List[int] = typer.Option(
        [],
        "-i",
        "--includeseq",
        help="Include this sequence only, can specify multiple times",
    ),
    skipseq: List[int] = typer.Option(
        [], "-s", "--skipseq", help="Exclude this sequence, can specify multiple times",
    ),
    log_id: str = datetime.now().strftime("%m-%d-%Y-%H-%M-%S"),
    verbose: bool = False,
    very_verbose: bool = False,
    cleanup: bool = False,
    overwrite: bool = False,
):
    """
    Export XNAT DICOM images in an experiment to a BIDS friendly format
    """

    bids_root_dir = os.path.expanduser(args.bids_root_dir)
    build_dir = os.getcwd()
    bidsmap = None

    # Parse bidsmap file
    if bidsmap_file is not None:
        bidsmap = json.load(f)

    # Set up working directory
    if not os.access(bids_root_dir, os.R_OK):
        raise ValueError(f"BIDS Root directory must exist: {bids_root_dir}")

    # Set up session
    connection = requests.Session()
    connection.verify = False
    connection.auth = (args.user, args.password)

    project, subject = get_project_and_subject_id(connection, host, session)

    pi_prefix, study_prefix, subject_prefix, session_prefix = prepare_bids_prefixes(
        project, subject, session_suffix
    )

    # Set up logging
    logs_dir = f"{bids_root_dir}/{pi_prefix}/{study_prefix}/logs"

    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    setup_logging(args.loglevel, f"{logs_dir}/export-{log_id}.log")

    # Export
    scans = get_scan_ids(connection, host, session)
    scans = filter_scans(scans, seqlist=seqlist, skiplist=skiplist)
    scans = bidsmap_scans(scans, bidsmap)

    assign_bids_name(
        connection, host, subject, session, scans, build_dir, export_session_dir,
    )

    # Close connection(I don't think this works)
    connection.delete(f"{host}/data/JSESSION")
    connection.close()

    return project, subject


@app.command()
def run_heudiconv(
    project: str,
    subject: str,
    session: str,
    bids_root_dir: str,
    session_suffix: str = "01",
    log_id: str = datetime.now().strftime("%m-%d-%Y-%H-%M-%S"),
    verbose: str = False,
    very_verbose: str = False,
    cleanup: str = False,
    overwrite: str = False,
):
    """
    Run Heudiconv
    """
    print("run Heudiconv")


@app.command()
def xnat2bids(
    user: str,
    password: str,
    session: str,
    bids_root_dir: str,
    host: str = "https://bnc.brown.edu/xnat",
    session_suffix: str = "01",
    bidsmap_file: str = "",
    includeseq: List[int] = typer.Option(
        [],
        "-i",
        "--includeseq",
        help="Include this sequence only, can specify multiple times",
    ),
    skipseq: List[int] = typer.Option(
        [], "-s", "--skipseq", help="Exclude this sequence, can specify multiple times",
    ),
    log_id: str = datetime.now().strftime("%m-%d-%Y-%H-%M-%S"),
    verbose: bool = False,
    very_verbose: bool = False,
    cleanup: bool = False,
    overwrite: bool = False,
):
    """
    Export DICOM images from an XNAT experiment to a BIDS compliant directory
    """

    print(includeseq)
    # project, subject = dicom_export(
    #     user,
    #     password,
    #     session,
    #     bids_root_dir,
    #     host=host,
    #     session_suffix=session_suffix,
    #     bidsmap_file=bidsmap_file,
    #     seqlist=seqlist,
    #     skiplist=skiplist,
    #     log_id=log_id,
    #     verbose=verbose,
    #     very_verbose=very_verbose,
    #     cleanup=cleanup,
    #     overwrite=overwrite,
    # )
    # run_heudiconv(
    #     session,
    #     project,
    #     subject,
    #     bids_root_dir,
    #     session_suffix=session_suffix,
    #     log_id=log_id,
    #     verbose=verbose,
    #     very_verbose=very_verbose,
    #     overwrite=overwrite,
    # )


if __name__ == "__main__":
    app()
