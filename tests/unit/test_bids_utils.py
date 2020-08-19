import os
import shutil
import pytest
import xnat_tools.bids_utils as utils

from xnat_tools.bids_utils import (
    handle_scanner_exceptions,
    bidsmap_scans,
    bidsify_dicom_headers,
)


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


def test_bidsify_dicom_headers(mocker):
    """Test bidsify_dicom_headers without ProtocolName field"""
    dataset = mocker.MagicMock()
    dataset.__contains__.return_value = False

    dcmread = mocker.patch("pydicom.dcmread")
    dcmread.return_value = dataset

    bidsify_dicom_headers("filename", "foo")

    assert dataset.data_element.called == False


def test_bidsify_dicom_headers_with_protocol_name(mocker):
    """Test bidsify_dicom_headers with ProtocolName match"""
    series_description = "foo"

    dataset = mocker.MagicMock()
    dataset.__contains__.return_value = True
    dataset.data_element.return_value = mocker.Mock(value=series_description)

    dcmread = mocker.patch("pydicom.dcmread")
    dcmread.return_value = dataset

    bidsify_dicom_headers("filename", series_description)

    dataset.data_element.assert_called_once_with("ProtocolName")


def test_bidsify_dicom_headers_with_protocol_name_mismatch(mocker):
    """Test bidsify_dicom_headers with ProtocolName mismatch"""
    series_description = "foo"
    protocol_name_mock = mocker.Mock(value="bar")
    series_description_mock = mocker.Mock(value="quux")

    side_effect = [
        protocol_name_mock,      # 1st call to check if the ProtocolName
        protocol_name_mock,      # 2nd call to set the ProtocolName
        series_description_mock, # 3rd call to set SeriesDescription
    ]

    dataset = mocker.MagicMock()
    dataset.__contains__.return_value = True
    dataset.data_element.side_effect = side_effect

    dcmread = mocker.patch("pydicom.dcmread")
    dcmread.return_value = dataset

    bidsify_dicom_headers("filename", series_description)

    print(dataset.data_element.mock_calls)
    dataset.data_element.assert_has_calls(
        [
            mocker.call("ProtocolName"),
            mocker.call("ProtocolName"),
            mocker.call("SeriesDescription"),
        ]
    )

    assert protocol_name_mock.value == series_description
    assert series_description_mock.value == series_description
