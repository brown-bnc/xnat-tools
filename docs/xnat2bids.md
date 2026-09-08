# `xnat2bids`

Export DICOM images from an XNAT experiment to a BIDS compliant directory

**Usage**:

```console
$ xnat2bids [OPTIONS] {session} {bids_root_dir}
```

**Arguments**:

* `session`: XNAT Session ID, that is the Accession # for an experiment.  [required]
* `bids_root_dir`: Root output directory for exporting the files  [required]

**Options**:

* `-u, --user <str>`: XNAT User
* `-p, --pass <str>`: XNAT Password
* `-h, --host <str>`: XNAT&#x27;sURL  [default: https://xnat.bnc.brown.edu]
* `-S, --session-suffix <str>`: The session_suffix is initially set to -1.              This will signify an unspecified session_suffix and default to sess-01.              For multi-session studies, the session label will be pulled from XNAT  [default: -1]
* `-f, --bidsmap-file <str>`: Bidsmap JSON file to correct sequence names
* `-i, --includeseq <str>`: Include this sequence only, this flag can specify multiple times
* `-s, --skipseq <str>`: Exclude this sequence, can be specified multiple times
* `--log-id <str>`: ID or suffix to append to logfile. If empty, current date is used  [default: current date - MM-DD-YYYY-HH-MM-SS]
* `-v, --verbose`: Verbose level. This flag can be specified multiple times to increase verbosity  [default: 0]
* `--overwrite`: Remove directories where prior results for this session/participant
* `--cleanup`: Remove xnat-export folder and move logs to derivatives/xnat/logs
* `--skip-export`: Skip DICOM Export, while only running BIDS conversion
* `--export-only`: Run DICOM Export without subsequent BIDS conversion
* `--validate_frames`: Validate the frame counts of all acquisitions of functional bold sequences. If the final acquisition does not contain the expected number of slices, the associated DICOM file will be deleted.
* `-d, --dicomfix-config <str>`: JSON file to correct DICOM fields. USE WITH CAUTION
* `--export-mode <int range>`: Export mode: 0 = export defaced if present, 1 = force non-defaced export, 2 = export both defaced and non-defaced  [default: 0; 0&lt;=x&lt;=2]
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.
