# `run_heudiconv`

Run Heudiconv

**Usage**:

```console
$ run_heudiconv [OPTIONS] PROJECT SUBJECT BIDS_ROOT_DIR
```

**Arguments**:

* `PROJECT`: XNAT&#x27;s Project ID  [required]
* `SUBJECT`: XNAT&#x27;s subject ID  [required]
* `BIDS_ROOT_DIR`: Root output directory for exporting files  [required]

**Options**:

* `-S, --session-suffix TEXT`: The session_suffix is initially set to -1.              This will signify an unspecified session_suffix and default to sess-01.              For multi-session studies, the session label will be pulled from XNAT  [default: -1]
* `--log-id TEXT`: ID or suffix to append to logfile. If empty, current date is used  [default: current date - MM-DD-YYYY-HH-MM-SS]
* `--overwrite / --no-overwrite`: Remove directories where prior results for session/participant may exist  [default: no-overwrite]
* `--cleanup / --no-cleanup`: Remove xnat-export folder and move logs to derivatives/xnat/logs  [default: no-cleanup]
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.
