import os
import glob
import shutil
import shlex
from dotenv import load_dotenv
from typer.testing import CliRunner
from xnat_tools.xnat2bids import app

runner = CliRunner()
load_dotenv()


def test_xnat2bids():
    """Integration test for xnat2bids executable"""

    xnat_user = os.environ.get("XNAT_USER", "testuser")
    xnat_pass = os.environ.get("XNAT_PASS", "")
    session = os.environ.get("XNAT_SESSION", "")
    session_suffix = os.environ.get("XNAT_SESSION_SUFFIX", "01")
    bids_root_dir = os.environ.get("XNAT_BIDS_ROOT", "./tests/xnat2bids")
    seqlist = ["1", "2", "3", "6"]
    skiplist = ["2", "3"]

    if os.path.exists(bids_root_dir):
        shutil.rmtree(bids_root_dir, ignore_errors=True)

    os.mkdir(bids_root_dir)

    xnat2bids_cmd = f"{session} {bids_root_dir} -u {xnat_user} -p {xnat_pass} \
                      -i {' -i '.join(seqlist)} -s {' -s '.join(skiplist)}"

    xnat2bids_split_cmd = shlex.split(xnat2bids_cmd)
    print(xnat2bids_split_cmd)
    r = runner.invoke(app, xnat2bids_split_cmd)
    print(r.stdout)

    assert r.exit_code == 0

    filepath = f"tests/xnat2bids/*/study-*/bids/sub-*/ses-{session_suffix}"

    # ***************************************************************************
    # Test for succesfull execution
    # ***************************************************************************
    assert len(glob.glob(f"{filepath}/*/*.json")) > 0
    assert len(glob.glob(f"{filepath}/*/*.nii.gz")) > 0

    # ***************************************************************************
    # Test for correctess of sequence number given by seqlist and skiplist
    # ***************************************************************************
    xnat_export_path = glob.glob(
        f"tests/xnat2bids/*/study-*/xnat-export/sub-*/ses-{session_suffix}"
    )[0]
    assert os.path.isdir(os.path.join(os.getcwd(), xnat_export_path))

    export_subdirs = [f.path for f in os.scandir(xnat_export_path) if f.is_dir()]

    for d in export_subdirs:
        for f in os.listdir(d):
            # print(f)
            dicom_sequence = int(f.split(".")[3])
            # print("------- Dicom sequence:")
            # print(dicom_sequence)
            assert str(dicom_sequence) in seqlist
            assert str(dicom_sequence) not in skiplist