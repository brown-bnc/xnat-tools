# `run_heudiconv`

Run Heudiconv

**Usage**:

```console
$ run_heudiconv [OPTIONS] PROJECT SUBJECT BIDS_ROOT_DIR
```

**Arguments**:

* `PROJECT`: XNAT's Project ID  [required]
* `SUBJECT`: XNAT's subject ID  [required]
* `BIDS_ROOT_DIR`: Root output directory for exporting files  [required]

**Options**:

* `-S, --session-suffix TEXT`: Suffix of the session for BIDS defaults to 01.              This will produce a session label of sess-01.              You likely only need to change the default for multi-session studies  [default: 01]
* `--log-id TEXT`: ID or suffix to append to logfile. If empty, current date is used  [default: current date - MM-DD-YYYY-HH-MM-SS]
* `--overwrite / --no-overwrite`: Remove directories where prior results for session/participant may exist  [default: False]
* `--cleanup / --no-cleanup`: Remove xnat-export folder and move logs to derivatives/xnat/logs  [default: False]
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.
