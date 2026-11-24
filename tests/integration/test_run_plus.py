import shlex

from typer.testing import CliRunner

from tests.helpers import reset_directory
from xnat_tools.xnat2bids import app

runner = CliRunner()


def test_run_plus(xnat_user, xnat_password, xnat_bids_root, test_session):
    """Integration test for sequence list"""

    # Reset the xnat_bids_root directory
    reset_directory(xnat_bids_root)

    # Define target session
    session_data, _, session_suffix_path_prefixes = test_session
    _, _, session, _ = session_data
    pi_path_prefix, project_path_prefix, subject_path_prefix, session_suffix_path_prefix = (
        session_suffix_path_prefixes
    )
    seqlist = ["10", "11"]
    skiplist = ["6"]

    # Run xnat2bids
    xnat2bids_cmd = shlex.split(
        f"{session} {xnat_bids_root} -u {xnat_user} -p {xnat_password} \
                      -i {' -i '.join(seqlist)} -s {' -s '.join(skiplist)}"
    )
    print("Running xnat2bids application:")
    r = runner.invoke(app, xnat2bids_cmd)
    print(r.stdout)

    # TODO: The study path here includes "BNC_" - the prefix needs to be stripped out
    # TODO: This is done in prepare_path_prefixes
    xnat_export_path = (
        xnat_bids_root
        / pi_path_prefix
        / project_path_prefix
        / "xnat-export"
        / subject_path_prefix
        / session_suffix_path_prefix
    )
    task_name = "func-bold_task-checks_run"

    assert xnat_export_path.is_dir()
    for i in range(1, len(seqlist) + 1):
        assert (xnat_export_path / f"{task_name}-{i:02}").is_dir()
