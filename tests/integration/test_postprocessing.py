import json
import os
import shlex
import shutil

from dotenv import load_dotenv
from typer.testing import CliRunner

from xnat_tools.bids_postprocess import bids_postprocess
from xnat_tools.xnat2bids import app as xnat2bids_app

runner = CliRunner()
load_dotenv()


def test_postprocessing():
    """Integration test for bids-postprocessing executable"""
    xnat_user = os.environ.get("XNAT_USER", "testuser")
    xnat_pass = os.environ.get("XNAT_PASS", "")
    session = "XNAT2_E00017"
    bids_root_dir = os.environ.get("XNAT_BIDS_ROOT", "./tests/xnat2bids")
    seqlist = ["19", "23", "24"]

    if os.path.exists(bids_root_dir):
        shutil.rmtree(bids_root_dir, ignore_errors=True)

    os.mkdir(bids_root_dir)

    xnat2bids_cmd = f"{session} {bids_root_dir} -u {xnat_user} -p {xnat_pass} \
                      -i {' -i '.join(seqlist)}"

    xnat2bids_split_cmd = shlex.split(xnat2bids_cmd)

    r = runner.invoke(xnat2bids_app, xnat2bids_split_cmd)
    print(r.stdout)

    bids_dir = "tests/xnat2bids/ashenhav/study-1222/bids"

    bids_postprocess(
        session,
        bids_dir,
        log_file="",
        session_suffix="01",
        includesubj=[9011, 9999, 111, 9999, 111],
        skipsubj=[9999, 111],
        verbose=0,
    )

    # lazy check for the intendedFor field in one json file
    json_file = f"{bids_dir}/sub-9011/ses-01/fmap/sub-9011_ses-01_acq-greAP_phasediff.json"

    with open(json_file, "r") as f:
        data = json.load(f)
        assert data["IntendedFor"] != ""
        f.close

    # cleanup output -- for debugging commsent this out
    shutil.rmtree(bids_root_dir, ignore_errors=True)

    # you can locally run bids-validator
    # bids_directory=${PWD}/tests/xnat2bids/ashenhav/study-1222/bids/
    # docker run -ti --rm -v ${bids_directory}:/data:ro bids/validator /data
