# `xnat_tools`

Export DICOM images from an XNAT experiment to a BIDS compliant directory

**Usage**:

```console
$ xnat_tools [OPTIONS] SESSION BIDS_ROOT_DIR
```

**Arguments**:

* `SESSION`: XNAT Session ID, that is the Accession # for an experiment.  [required]
* `BIDS_ROOT_DIR`: Root output directory for exporting the files  [required]

**Options**:

* `-u, --user TEXT`: XNAT User
* `-p, --pass TEXT`: XNAT Password
* `-h, --host TEXT`: XNAT'sURL  [default: https://bnc.brown.edu/xnat]
* `-S, --session-suffix TEXT`: Suffix of the session for BIDS defaults to 01.              This will produce a session label of sess-01.              You likely only need to change the default for multi-session studies  [default: 01]
* `-f, --bidsmap-file TEXT`: Bidsmap JSON file to correct sequence names  [default: ]
* `-i, --includeseq INTEGER`: Include this sequence only, can specify multiple times  [default: ]
* `-s, --skipseq INTEGER`: Exclude this sequence, can be specified multiple times  [default: ]
* `--log-id TEXT`: ID or suffix to append to logfile, If empty, date is appended  [default: 10-21-2020-19-01-24]
* `-v, --verbose`: Verbose level. Can be specified multiple times to increase verbosity  [default: 0]
* `--overwrite`: Remove directories where prior results for this session/participant  [default: False]
* `--cleanup / --no-cleanup`: Remove xnat-export folder and move logs to derivatives/xnat/logs  [default: False]
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.
