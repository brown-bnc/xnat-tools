import os
import shlex

from typer.testing import CliRunner

from tests.helpers import reset_directory
from xnat_tools.xnat2bids import app

runner = CliRunner()


def test_run_plus(xnat_user, xnat_password, xnat_bids_root):
    """Integration test for sequence list"""

    # Define target session
    session = "XNAT_E00114"
    session_suffix = "session1"

    # Reset the xnat_bids_root directory
    reset_directory(xnat_bids_root)

    seqlist = ["10", "11"]
    skiplist = ["6"]
    xnat2bids_cmd = shlex.split(
        f"{session} {xnat_bids_root} -u {xnat_user} -p {xnat_password} \
                      -i {' -i '.join(seqlist)} -s {' -s '.join(skiplist)}"
    )
    print("Running xnat2bids application:")
    r = runner.invoke(app, xnat2bids_cmd)
    print(r.stdout)

    xnat_export_path = (
        f"{xnat_bids_root}/bnc/study-demodat/xnat-export/sub-005/ses-{session_suffix}/"
    )
    task_name = "func-bold_task-checks_run"

    assert os.path.isdir(os.path.join(os.getcwd(), xnat_export_path))
    for i in range(1, len(seqlist) + 1):
        assert os.path.isdir(os.path.join(os.getcwd(), xnat_export_path, f"{task_name}-{i:02}"))
