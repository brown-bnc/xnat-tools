# `bids_postprocess`

Script for performing post BIDSIFY processing.
At the moment it inserts the IntendedFor field
to JSON sidecart for fieldmap data

**Usage**:

```console
$ bids_postprocess [OPTIONS] SESSION BIDS_EXPERIMENT_DIR
```

**Arguments**:

* `SESSION`: XNAT Session ID, that is the Accession # for an experiment.  [required]
* `BIDS_EXPERIMENT_DIR`: Root output directory for exporting the files  [required]

**Options**:

* `-S, --session-suffix TEXT`: Suffix of the session for BIDS defaults to 01.         This will produce a session label of sess-01.         You likely only need to change the default for multi-session studies  [default: 01]
* `-i, --includesubj TEXT`: Include this participant only, this flag can be specified multiple times  [default: ]
* `-s, --skipsubj TEXT`: Skip this participant, this flag can be specified multiple times  [default: ]
* `--log-file TEXT`: File to send logs to  [default: ]
* `-v, --verbose`: Verbosity level. This flag can be specified multiple times to increase verbosity  [default: 0]
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.
