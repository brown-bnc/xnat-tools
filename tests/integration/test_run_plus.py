import os
import shlex
import shutil

from dotenv import load_dotenv
from typer.testing import CliRunner

from xnat_tools.xnat2bids import app

load_dotenv()
runner = CliRunner()


def test_run_plus():
    """Integration test for sequence list"""
    xnat_user = os.environ.get("XNAT_USER", "")
    xnat_pass = os.environ.get("XNAT_PASS", "")
    session = "XNAT_E00114"
    session_suffix = "session1"
    bids_root_dir = os.environ.get("XNAT_BIDS_ROOT", "./tests/xnat2bids")
    seqlist = ["10", "11"]
    skiplist = ["6"]

    if os.path.exists(bids_root_dir):
        shutil.rmtree(bids_root_dir, ignore_errors=True)

    os.mkdir(bids_root_dir)

    xnat2bids_cmd = f"{session} {bids_root_dir} -u {xnat_user} -p {xnat_pass} \
                      -i {' -i '.join(seqlist)} -s {' -s '.join(skiplist)}"

    xnat2bids_split_cmd = shlex.split(xnat2bids_cmd)

    r = runner.invoke(app, xnat2bids_split_cmd)
    print(r.stdout)

    xnat_export_path = (
        f"tests/xnat2bids/bnc/study-demodat/xnat-export/sub-005/ses-{session_suffix}/"
    )
    task_name = "func-bold_task-checks_run"

    assert os.path.isdir(os.path.join(os.getcwd(), xnat_export_path))
    for i in range(1, len(seqlist) + 1):
        assert os.path.isdir(os.path.join(os.getcwd(), xnat_export_path, f"{task_name}-{i:02}"))

    # cleanup output -- for debugging comment this out
    shutil.rmtree(bids_root_dir, ignore_errors=True)
