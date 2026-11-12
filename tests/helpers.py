import os
import shutil


def series_idx(f):
    """Return series index from filename"""
    ext = f.split(".")[-1]
    if ext == "dcm":
        return f.split("-")[1]
    elif ext == "IMA":
        return f.split(".")[3]
    else:
        return 0


def reset_directory(path):
    """Delete and recreate a directory. Use to reset xnat_bids_root between tests"""
    shutil.rmtree(path, ignore_errors=True)
    os.makedirs(path, exist_ok=True)
