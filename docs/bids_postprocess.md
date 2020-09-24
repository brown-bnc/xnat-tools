# `bids-postprocess`

Script for performing post BIDSIFY processing. 
At the moment it inserts the IntendedFor field to JSON sidecart for fieldmap data

**Usage**:

```console
$ bids-postprocess [OPTIONS] SESSION BIDS_EXPERIMENT_DIR
```

**Arguments**:

* `SESSION`: XNAT Session ID, that is the Accession # for an experiment.  [required]
* `BIDS_EXPERIMENT_DIR`: Root output directory for exporting the files  [required]

**Options**:

* `-ss, --session-suffix TEXT`: Suffix of the session for BIDS defaults to 01. This will produce a session label of sess-01. You likely only need to change the dault for multi-session studies  [default: 01]
* `-i, --includeseq INTEGER`: Include this participant only, can be specified multiple times  [default: ]
* `-s, --skipseq INTEGER`: Skip this participant, can be specified multiple times  [default: ]
* `--log-file TEXT`: File to senf logs to  [default: ]
* `-v`: Verbose logging. If True, sets loglevel to INFO  [default: False]
* `--vv`: Very verbose logging. If True, sets loglevel to DEBUG  [default: False]
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.
