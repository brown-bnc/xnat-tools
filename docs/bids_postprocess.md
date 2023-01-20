# `bids_postprocess`

Script for performing post BIDSIFY processing.
At the moment it inserts the IntendedFor field
to JSON sidecart for fieldmap data

**Usage**:

```console
$ bids_postprocess [OPTIONS] BIDS_EXPERIMENT_DIR
```

**Arguments**:

* `BIDS_EXPERIMENT_DIR`: Root output directory for exporting the files  [required]

**Options**:

* `-u, --user TEXT`: XNAT User
* `-p, --pass TEXT`: XNAT Password
* `--session TEXT`: XNAT Session ID, that is the Accession # for an experiment.  [default: ]
* `-is, --includesess TEXT`: Include this session only, this flag can be specified multiple time  [default: ]
* `-i, --includesubj TEXT`: Include this participant only, this flag can be specified multiple times  [default: ]
* `-s, --skipsubj TEXT`: Skip this participant, this flag can be specified multiple times  [default: ]
* `--log-file TEXT`: File to send logs to  [default: ]
* `-v, --verbose`: Verbosity level. This flag can be specified multiple times to increase verbosity  [default: 0]
* `--overwrite`: Inititate BIDS post-processing on all subjects located at the specified BIDS             directory, with intent to ovewrite existing data.  [default: False]
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.
