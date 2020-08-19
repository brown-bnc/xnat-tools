import os
import shutil
import xnat_tools.bids_utils as utils

from xnat_tools.bids_utils import handle_scanner_exceptions, bidsmap_scans


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


def test_handle_scanner_exceptions():
    """Test handle_scanner_exceptions"""
    # It should uppercase the t in t1w and t2w
    assert handle_scanner_exceptions("foo_t1w") == "foo_T1w"
    assert handle_scanner_exceptions("foo_t2w") == "foo_T2w"

    # It should remove bonus underscores from aascout planes
    assert handle_scanner_exceptions("foo_MPR_sag") == "fooMPRsag"
    assert handle_scanner_exceptions("foo_MPR_cor") == "fooMPRcor"
    assert handle_scanner_exceptions("foo_MPR_tra") == "fooMPRtra"

    # It should remove spaces near RMS
    assert handle_scanner_exceptions("foo RMS") == "fooRMS"


def test_bidsmap_scans():
    """Test bidsmap_scans without bidsmap data"""
    scans = [(f"{i}", f"scan_{i:02}") for i in range(1, 11)]

    assert bidsmap_scans(scans) == scans


def test_bidsmap_scans_simple_replacement():
    """Test bidsmap_scans with a simple bidsmap replacement"""
    bidsmap = [{"series_description": "foo 1", "bidsname": "bar 1"}]
    scans = [("1", "foo 1"), ("2", "quux 2")]

    assert bidsmap_scans(scans, bidsmap) == [("1", "bar 1"), ("2", "quux 2")]


def test_bidsmap_scans_scanner_exception():
    """Test bidsmap_scans with scanner exceptions"""
    scans = [("1", "foo_t1w")]

    # NOTE (BNR): What we're really testing here is that handle_scanner_exceptions
    #             gets called. We could do that with a mock, but I think this is
    #             good enough. The reason I'm not enumerating the exceptions here
    #             is because I _only_ care if handle_scanner_exceptions gets called. 
    #             Enumerating the different cases will not yield a better test here.
    assert bidsmap_scans(scans) == [("1", "foo_T1w")]


def test_bidsmap_scans_run_plus():
    """Test bidsmap_scans with run+ series descriptions"""
    scans = [("1", "run+"), ("2", "run+"), ("3", "run+")]

    assert bidsmap_scans(scans) == [("1", "run-01"), ("2", "run-02"), ("3", "run-03")]