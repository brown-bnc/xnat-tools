import shlex

from typer.testing import CliRunner

from tests.helpers import reset_directory, series_idx
from xnat_tools.dicom_export import app as export_app
from xnat_tools.dicom_export import dicom_export
from xnat_tools.run_heudiconv import app as heudi_app

runner = CliRunner()


# TODO: Should this be split into smaller tests?
def test_dicom_export(xnat_user, xnat_password, xnat_bids_root, xnat_host, test_session):
    """Integration test for xnat-dicom-export"""

    # Reset the xnat_bids_root directory
    reset_directory(xnat_bids_root)

    # Define target session
    session_data, session_data_clean, session_suffix_path_prefixes = test_session
    _, _, session, session_suffix = session_data
    project_clean, subject_clean, session_suffix_clean = session_data_clean
    pi_path_prefix, project_path_prefix, subject_path_prefix, session_suffix_path_prefix = (
        session_suffix_path_prefixes
    )
    export_dir = (
        xnat_bids_root
        / pi_path_prefix
        / project_path_prefix
        / "xnat-export"
        / subject_path_prefix
        / session_suffix_path_prefix
    )

    # ***************************************************************************
    # Test for successful execution
    # Here we call the function directly. Note, that at the moment, when calling
    # the function, the default values are not correct.
    # See https://github.com/tiangolo/typer/issues/106
    # ***************************************************************************

    p, s, ss = dicom_export(
        session,
        str(xnat_bids_root),
        user=xnat_user,
        password=xnat_password,
        host=xnat_host,
        session_suffix=session_suffix,
        bidsmap_file="",
        # TODO?: Is this specific to the old session? Or can it be used for everything?
        includeseq=["10"],
        skipseq=[],
        log_id="pytest",
        verbose=0,
        overwrite=False,
        validate_frames=False,
        correct_dicoms_config="",
    )

    assert p == project_clean
    assert s == subject_clean
    assert ss == session_suffix_clean

    assert any(export_dir.glob("*/*.IMA")) or any(export_dir.glob("*/*.dcm"))

    subdirs = [d for d in export_dir.iterdir() if d.is_dir()]
    assert len(subdirs) == 1
    for d in subdirs:
        for f in d.iterdir():
            idx = series_idx(f.name)
            assert idx == "10"

    # ***************************************************************************
    # Test that default overwrite flag is NOT wiping the xnat-export directory
    # Here we test using typer's CLIRunner
    # ***************************************************************************

    export_cmd = shlex.split(
        f"{session} {xnat_bids_root} -u {xnat_user} -p {xnat_password} -i 8 -v"
    )
    print("Running dicom_export application:")
    r = runner.invoke(export_app, export_cmd)
    print(r.stdout)

    subdirs = [d for d in export_dir.iterdir() if d.is_dir()]

    assert len(subdirs) == 2
    for d in subdirs:
        for f in d.iterdir():
            idx = series_idx(f.name)
            assert idx in ["8", "10"]

    # # ***************************************************************************
    # # Test that overwrite flag is wiping the xnat-export directory
    # # ***************************************************************************

    export_cmd = shlex.split(
        f"{session} {xnat_bids_root} -u {xnat_user} -p {xnat_password} -v -i 10 --overwrite"
    )
    print("Running dicom_export application:")
    r = runner.invoke(export_app, export_cmd)
    print(r.stdout)

    subdirs = [d for d in export_dir.iterdir() if d.is_dir()]

    assert len(subdirs) == 1

    for d in subdirs:
        for f in d.iterdir():
            idx = series_idx(f.name)
            assert idx == "10"


# TODO: Should this be split into smaller tests?
def test_heudiconv(xnat_bids_root, test_session):
    """Integration test for running the run-heudiconv executable on the output
    of xnat-dicom-export"""

    # TODO #186: This test relies on the previous test (test_dicom_export) seeding the
    # TODO #186: xnat_bids_root directory. This needs to seed its own dicom export to be independent

    # Define target session
    session_data, _, session_suffix_path_prefixes = test_session
    project, subject, _, session_suffix = session_data
    pi_path_prefix, project_path_prefix, subject_path_prefix, session_suffix_path_prefix = (
        session_suffix_path_prefixes
    )

    # Run run_heudiconv
    run_heudiconv_cmd = shlex.split(
        f"{project} {subject} {xnat_bids_root} --session-suffix {session_suffix}"
    )
    print("Running run_heudiconv application:")
    r = runner.invoke(heudi_app, run_heudiconv_cmd)
    print(r.stdout)

    # ***************************************************************************
    # Test for successful execution
    # ***************************************************************************

    assert r.exit_code == 0

    bids_session_dir = (
        xnat_bids_root
        / pi_path_prefix
        / project_path_prefix
        / "bids"
        / subject_path_prefix
        / session_suffix_path_prefix
    )
    assert any(bids_session_dir.glob("*/*.json")) or any(bids_session_dir.glob("*/*.nii.gz"))

    # # ***************************************************************************
    # # Test for RuntimeError Heudiconv doesn't allow overwrite
    # # ***************************************************************************

    run_heudiconv_cmd = shlex.split(
        f"{project} {subject} {xnat_bids_root} --session-suffix {session_suffix}"
    )
    print("Running run_heudiconv application:")
    r = runner.invoke(heudi_app, run_heudiconv_cmd)
    print(r.stdout)

    assert r.exit_code == 1

    # # ***************************************************************************
    # # Test overwrite is working
    # # ***************************************************************************

    run_heudiconv_cmd = shlex.split(
        f"{project} {subject} {xnat_bids_root} --session-suffix {session_suffix} --overwrite"
    )
    print("Running run_heudiconv application:")
    r = runner.invoke(heudi_app, run_heudiconv_cmd)
    print(r.stdout)

    assert r.exit_code == 0
