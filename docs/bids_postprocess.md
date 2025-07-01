# `bids_postprocess`

Script for performing post BIDSIFY processing.
At the moment it inserts the IntendedFor field
to JSON sidecar for fieldmap data, and removes
the AcquisitionDuration key from func jsons if
RepetitionTime is present, because they are
mutually exclusive according to BIDS spec

**Usage**:

```console
$ bids_postprocess [OPTIONS] BIDS_EXPERIMENT_DIR
```

**Arguments**:

* `BIDS_EXPERIMENT_DIR`: Root output directory for exporting the files  [required]

**Options**:

* `-u, --user TEXT`: XNAT User
* `-p, --pass TEXT`: XNAT Password
* `--session TEXT`: XNAT Session ID, that is the Accession # for an experiment.
* `-n, --includesess TEXT`: Include this session only, this flag can be specified multiple time
* `-i, --includesubj TEXT`: Include this participant only, this flag can be specified multiple times
* `-s, --skipsubj TEXT`: Skip this participant, this flag can be specified multiple times
* `-k, --skipsess TEXT`: Skip this session, this flag can be specified multiple times
* `--log-file TEXT`: File to send logs to
* `-v, --verbose`: Verbosity level. This flag can be specified multiple times to increase verbosity  [default: 0]
* `--overwrite`: Inititate BIDS post-processing on all subjects located at the specified BIDS             directory, with intent to ovewrite existing data.
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.
