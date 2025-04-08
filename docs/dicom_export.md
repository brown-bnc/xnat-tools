# `dicom_export`

Export XNAT DICOM images in an experiment to a BIDS friendly format

**Usage**:

```console
$ dicom_export [OPTIONS] SESSION BIDS_ROOT_DIR
```

**Arguments**:

* `SESSION`: XNAT Session ID, that is the Accession # for an experiment.  [required]
* `BIDS_ROOT_DIR`: Root output directory for exporting the files  [required]

**Options**:

* `-u, --user TEXT`: XNAT User
* `-p, --pass TEXT`: XNAT Password
* `-h, --host TEXT`: XNAT&#x27;s URL  [default: https://xnat.bnc.brown.edu]
* `-S, --session-suffix TEXT`: The session_suffix is initially set to -1.              This will signify an unspecified session_suffix and default to sess-01.              For multi-session studies, the session label will be pulled from XNAT  [default: -1]
* `-f, --bidsmap-file TEXT`: Bidsmap JSON file to correct sequence names
* `-i, --includeseq TEXT`: Include this sequence only, this flag can specify multiple times
* `-s, --skipseq TEXT`: Exclude this sequence, this flag can specify multiple times
* `--log-id TEXT`: ID or suffix to append to logfile. If empty, current date is used  [default: current date - MM-DD-YYYY-HH-MM-SS]
* `-v, --verbose`: Verbose level. Can be specified multiple times to increase verbosity  [default: 0]
* `--overwrite`: Remove directories where prior results for session/participant may exist
* `--validate_frames`: Validate frame counts for all BOLD sequence acquisitions. Deletes the DICOM file if the final acquisition lacks expected slices.
* `-d, --dicomfix-config TEXT`: JSON file to correct DICOM fields. USE WITH CAUTION
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.
