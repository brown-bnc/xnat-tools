def series_idx(f):
    """Return series index from filename"""
    ext = f.split(".")[-1]
    if ext == "dcm":
        return f.split("-")[1]
    elif ext == "IMA":
        return f.split(".")[3]
    else:
        return 0
