import os

import pytest
from dotenv import load_dotenv

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
    xnat_bids_root = os.environ.get("XNAT_BIDS_ROOT", "tests/xnat2bids")

    return xnat_bids_root


@pytest.fixture
def demodat_session():
    """Legacy BNC demo session: project, subject, session, session_suffix"""
    return (
        # TODO: The values here are UPPER_CASE in XNAT but the callers use them in globs
        # TODO: The globs should lowercase them as that's something the code actually does
        os.environ.get("XNAT_PROJECT", "bnc_demodat"),
        os.environ.get("XNAT_SUBJECT", "005"),
        os.environ.get("XNAT_SESSION", "XNAT_E00114"),
        os.environ.get("XNAT_SESSION_SUFFIX", "session1"),
    )


@pytest.fixture
def demodat_session2():
    """Legacy BNC demo session: project, subject, session, session_suffix"""
    return (
        # TODO: The values here are UPPER_CASE in XNAT but the callers use them in globs
        # TODO: The globs should lowercase them as that's something the code actually does
        os.environ.get("XNAT_PROJECT", "bnc_demodat"),
        os.environ.get("XNAT_SUBJECT", "005"),
        os.environ.get("XNAT_SESSION", "XNAT_E00152"),
        os.environ.get("XNAT_SESSION_SUFFIX", "session2"),
    )


@pytest.fixture
def eeg_session():
    """BNC Test Session with EEG data: project, subject, session, session_suffix"""
    return (
        os.environ.get("XNAT_PROJECT", "BNC_XNATTEST"),
        os.environ.get("XNAT_SUBJECT", "BNC_METHODS"),
        os.environ.get("XNAT_SESSION", "XNAT_E00474"),
        os.environ.get("XNAT_SESSION_SUFFIX", "01"),
    )


@pytest.fixture
def xnat_host():
    return "https://xnat.bnc.brown.edu"


@pytest.fixture
def fake_host():
    return "https://example.com/xnat"
