import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

from xnat_tools.bids_utils import path_string_preprocess, prepare_path_prefixes

# Pytest will load this file before any of the tests automatically
# The test fixtures are "asked for" by each test that needs them

load_dotenv()


@pytest.fixture
def xnat_user():
    """The XNAT username to authenticate with"""
    return os.environ.get("XNAT_USER", "")


@pytest.fixture
def xnat_password():
    """The XNAT password to authenticate with"""
    return os.environ.get("XNAT_PASS", "")


@pytest.fixture
def xnat_bids_root():
    """The root directory to store the bids data"""
    # TODO: This should be at the root of the repository
    return Path(os.environ.get("XNAT_BIDS_ROOT", "tests/xnat2bids"))


@pytest.fixture
def test_session():
    """Test BNC demo session: project, subject, session, session_suffix"""
    project = os.environ.get("XNAT_PROJECT", "BNC_XNATTEST")
    subject = os.environ.get("XNAT_SUBJECT", "005")
    session_id = os.environ.get("XNAT_SESSION", "XNAT_E03533")
    session_suffix = os.environ.get("XNAT_SESSION_SUFFIX", "SESSION1")

    # The relevant session data
    session = (project, subject, session_id, session_suffix)
    # The cleaned session data
    session_data_clean = path_string_preprocess(project, subject, session_suffix)

    # The directory names of each piece of session data
    # TODO: This is not always a directory, sometimes part of a filename
    # TODO: We need a better name for it
    session_suffix_path_prefixes = prepare_path_prefixes(*session_data_clean)

    return (session, session_data_clean, session_suffix_path_prefixes)


@pytest.fixture
def test_session2():
    """Test BNC demo session: project, subject, session, session_suffix"""
    return (
        # TODO: The values here are UPPER_CASE in XNAT but the callers use them in globs
        # TODO: The globs should lowercase them as that's something the code actually does
        os.environ.get("XNAT_PROJECT", "bnc_xnattest"),
        os.environ.get("XNAT_SUBJECT", "005"),
        os.environ.get("XNAT_SESSION", "XNAT_E03534"),
        os.environ.get("XNAT_SESSION_SUFFIX", "session2"),
    )


@pytest.fixture
def eeg_session():
    """BNC Test Session with EEG data: project, subject, session, session_suffix"""
    return (
        os.environ.get("XNAT_PROJECT", "BNC_XNATTEST"),
        os.environ.get("XNAT_SUBJECT", "BNC_METHODS"),
        os.environ.get("XNAT_SESSION", "XNAT_E03532"),
        os.environ.get("XNAT_SESSION_SUFFIX", "01"),
    )


@pytest.fixture
def xnat_host():
    return "https://xnat.bnc.brown.edu"


@pytest.fixture
def fake_host():
    return "https://example.com/xnat"
