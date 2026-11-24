# `bids_postprocess`

Script for performing post BIDSIFY processing.
At the moment it inserts the IntendedFor field
to JSON sidecar for fieldmap data, and removes
the AcquisitionDuration key from func jsons if
RepetitionTime is present, because they are
mutually exclusive according to BIDS spec

**Usage**:

```console
$ bids_postprocess [OPTIONS] {bids_experiment_dir}
```

**Arguments**:

* `bids_experiment_dir <str>`: Root output directory for exporting the files  [required]

**Options**:

* `-u, --user <str>`: XNAT User
* `-p, --pass <str>`: XNAT Password
* `-h, --host <str>`: XNAT&#x27;s URL  [default: https://xnat.bnc.brown.edu]
* `--session <str>`: XNAT Session ID, that is the Accession # for an experiment.
* `-n, --includesess <list[str]>`: Include this session only, this flag can be specified multiple time
* `-i, --includesubj <list[str]>`: Include this participant only, this flag can be specified multiple times
* `-s, --skipsubj <list[str]>`: Skip this participant, this flag can be specified multiple times
* `-k, --skipsess <list[str]>`: Skip this session, this flag can be specified multiple times
* `--log-file <str>`: File to send logs to
* `-v, --verbose`: Verbosity level. This flag can be specified multiple times to increase verbosity  [default: 0]
* `--overwrite`: Inititate BIDS post-processing on all subjects located at the specified BIDS             directory, with intent to ovewrite existing data.
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.
