# `xnat2bids`

Export DICOM images from an XNAT experiment to a BIDS compliant directory

**Usage**:

```console
$ xnat2bids [OPTIONS] SESSION BIDS_ROOT_DIR
```

**Arguments**:

* `SESSION`: XNAT Session ID, that is the Accession # for an experiment.  [required]
* `BIDS_ROOT_DIR`: Root output directory for exporting the files  [required]

**Options**:

* `-u, --user TEXT`: XNAT User
* `-p, --pass TEXT`: XNAT Password
* `-h, --host TEXT`: XNAT'sURL  [default: https://xnat.bnc.brown.edu]

* `-S, --session-suffix TEXT`: The session_suffix is initially set to -1.              This will signify an unspecified session_suffix and default to sess-01.              For multi-session studies, the session label will be pulled from XNAT  [default: -1]
* `-f, --bidsmap-file TEXT`: Bidsmap JSON file to correct sequence names  [default: ]
* `-i, --includeseq INTEGER`: Include this sequence only, this flag can specify multiple times  [default: ]
* `-s, --skipseq INTEGER`: Exclude this sequence, can be specified multiple times  [default: ]
* `--log-id TEXT`: ID or suffix to append to logfile. If empty, current date is used  [default: current date - MM-DD-YYYY-HH-MM-SS]
* `-v, --verbose`: Verbose level. This flag can be specified multiple times to increase verbosity  [default: 0]
* `--overwrite`: Remove directories where prior results for this session/participant  [default: False]
* `--cleanup / --no-cleanup`: Remove xnat-export folder and move logs to derivatives/xnat/logs  [default: False]
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.
