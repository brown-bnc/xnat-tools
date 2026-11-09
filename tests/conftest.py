import os
import shutil

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
    # TODO: THis is going to make a different subfolder? How to make it in the base?
    # xnat_bids_root = os.environ.get("XNAT_BIDS_ROOT", "./tests/xnat2bids")
    xnat_bids_root = os.environ.get("XNAT_BIDS_ROOT", "tests/xnat2bids")

    # Clean directory if it exists before the tests start
    shutil.rmtree(xnat_bids_root, ignore_errors=True)
    os.mkdir(xnat_bids_root)
    return xnat_bids_root


@pytest.fixture
def xnat_host():
    return "https://xnat.bnc.brown.edu"


@pytest.fixture
def fake_host():
    return "https://example.com/xnat"
