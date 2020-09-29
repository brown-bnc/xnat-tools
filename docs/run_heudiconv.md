# `xnat-heudiconv`

Run Heudiconv

**Usage**:

```console
$ xnat-heudiconv [OPTIONS] PROJECT SUBJECT SESSION BIDS_ROOT_DIR
```

**Arguments**:

* `PROJECT`: XNAT's Project ID  [required]
* `SUBJECT`: XNAT's subject ID  [required]
* `SESSION`: XNAT's Session ID, i.e., Accession # for an experiment  [required]
* `BIDS_ROOT_DIR`: Root output directory for exporting the files  [required]

**Options**:

* `-ss, --session-suffix TEXT`: Suffix of the session for BIDS defaults to 01. This will produce a session label of sess-01. You likely only need to change the dault for multi-session studies  [default: 01]
* `--log-id TEXT`: ID or suffix to append to logfile, If empty, date is appended  [default: 09-24-2020-10-38-46]
* `-v`: Verbose logging. If True, sets loglevel to INFO  [default: False]
* `--vv`: Very verbose logging. If True, sets loglevel to DEBUG  [default: False]
* `--overwrite / --no-overwrite`: If True, remove directories where prior results for session/participant may exist  [default: False]
* `--cleanup / --no-cleanup`: If True, Remove xnat-export folder and move logs to derivatives/xnat/logs inside bids directory  [default: False]
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.