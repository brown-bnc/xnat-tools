import os
import shutil
import xnat_tools.bids_utils as utils


def test_prepare_export_output_path():
    """Unit test to create export output directory and using overwrite flag"""

    root_dir = "tests/unit/testdir"
    pi_prefix = "testpi"
    study_prefix = "teststudy"
    subject_prefix = "testp"
    session_prefix = "01"
    overwrite = False

    export_dir = utils.prepare_export_output_path(
        root_dir, pi_prefix, study_prefix, subject_prefix, session_prefix, overwrite
    )

    testfile = f"{export_dir}/deleteme"
    with open(testfile, "a") as file:
        file.write("deleteme")

    assert os.path.exists(testfile)
    overwrite = True
    export_dir = utils.prepare_export_output_path(
        root_dir, pi_prefix, study_prefix, subject_prefix, session_prefix, overwrite
    )
    assert not os.path.exists(testfile)

    # cleanup output
    shutil.rmtree(root_dir, ignore_errors=True)
