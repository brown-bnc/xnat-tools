# `dicom_export`

Export XNAT DICOM images in an experiment to a BIDS friendly format

**Usage**:

```console
$ dicom_export [OPTIONS] {session} {bids_root_dir}
```

**Arguments**:

* `session`: XNAT Session ID, that is the Accession # for an experiment.  [required]
* `bids_root_dir`: Root output directory for exporting the files  [required]

**Options**:

* `-u, --user <str>`: XNAT User
* `-p, --pass <str>`: XNAT Password
* `-h, --host <str>`: XNAT&#x27;s URL  [default: https://xnat.bnc.brown.edu]
* `-S, --session-suffix <str>`: The session_suffix is initially set to -1.              This will signify an unspecified session_suffix and default to sess-01.              For multi-session studies, the session label will be pulled from XNAT  [default: -1]
* `-f, --bidsmap-file <str>`: Bidsmap JSON file to correct sequence names
* `-i, --includeseq <str>`: Include this sequence only, this flag can specify multiple times
* `-s, --skipseq <str>`: Exclude this sequence, this flag can specify multiple times
* `--log-id <str>`: ID or suffix to append to logfile. If empty, current date is used  [default: current date - MM-DD-YYYY-HH-MM-SS]
* `-v, --verbose`: Verbose level. Can be specified multiple times to increase verbosity  [default: 0]
* `--overwrite`: Remove directories where prior results for session/participant may exist
* `--validate_frames`: Validate frame counts for all BOLD sequence acquisitions. Deletes the DICOM file if the final acquisition lacks expected slices.
* `-d, --dicomfix-config <str>`: JSON file to correct DICOM fields. USE WITH CAUTION
* `--force-non-defaced`: Export original DICOM when REFACED_DICOM is available
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.
