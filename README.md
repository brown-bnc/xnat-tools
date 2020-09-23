# XNAT Tools

XNAT tools maintained by the Behavioral Neuroimaging Center for the Brown University MRI users. In this README we summarize

1. [Installation](#Installatio)
2. [XNAT2BIDS](#XNAT2BIDS)

Additional instructions for the Brown University Community is available on the [BNC User Manual](docs.ccv.brown.edu/)

## Installation

### Using Docker

```
docker pull docker pull brownbnc/xnat_tools:<version>
```

_Version:_

- `latest`: Is the build of master
- `vX.X.X`: Latest tagged stable release

You can confirm the tags [here](https://hub.docker.com/repository/docker/brownbnc/xnat_tools/tags?page=1)

### Python

### Prerequisites:

We first need to install the dcm2niix . This is a dependency of Heudiconv, that doesn't get installed by Heudiconv itself

```
brew install dcm2niix
```

### Poetry

This package is developed using [Poetry](https://python-poetry.org). If you are familiar with Poetry, you can add it to your project via

```
poetry add git+https://github.com/brown-bnc/xnat-tools.git
```

or for a tagged release

```
poetry add git+https://github.com/brown-bnc/xnat-tools.git@v0.1.0-beta
```

You can also install xnat_tools using the python package manager of your choice. For instance:

#### PIP

- A Tagged Release

```
pip install git+https://github.com/brown-bnc/xnat-tools.git@v0.1.0-beta
```

- Development (Master branch)

```
pip install git+https://github.com/brown-bnc/xnat-tools.git
```

#### PIPX

If you are using this package in a stand-alone fashion, and you don't want to use Docker, we recommend using pipx. Please check their [installation instructions](https://github.com/pipxproject/pipx).

Once pipx is installed you install as follows:

A Tagged Release

```
pipx install git+https://github.com/brown-bnc/xnat-tools.git@v0.1.0-beta
```

Development (Master branch)

```
pipx install git+https://github.com/brown-bnc/xnat-tools.git
```

## XNAT2BIDS

In order to export data from XNAT and convert it in one step you can use the `xnat2bids` script part of this package.

After installation, the console script `xnat2bids` is available in your system. You can invoke it from the terminal as follows:

```
xnat_user=<user>
session=<xnat_accession_number>
bids_root_dir="~/data/bids-export"

xnat2bids --user ${xnat_user}  --session ${session} \
--bids_root_dir ${bids_root_dir}
```

### Understanding the inputs

Familiarize yourself with the inputs to xnat2bids
For a full list of the inputs, you can run:

```
 xnat2bids --help
```

Some key optional inputs to be aware of:

- `--bidsmap_file`: `xnat2bids` can take a json file with a dictionary of sequence names to correct/change. For instance you can pass `--bidsmap_file ./my_bidsmap.json`. The bidsmaps directory in this repository has examples of bidsmaps file
- `--seqlist`: If you only want to export some sequences from XNAT, you can pass the list (use order in your XNAT). e.g., `--seqlist 1 2 3 4 5 7 8 9`
- `--cleanup`: At the end on the process, the source data is avaialable in two directories `root_dir/xnat-export` and `root_dir/bids/sourcedata`. Passing the `--cleanup` flag removes `root_dir/xnat-export`

### Understanding the process

`xnat2bids` performs two main steps:

1. Export to a [Heudiconv](https://github.com/nipy/heudiconv) friendly directory structure. We follow the structure suggested by [the ReproIn guide](https://github.com/ReproNim/reproin), enabling us to use their [heuristic file](https://github.com/nipy/heudiconv/blob/master/heudiconv/heuristics/reproin.py).This step is encapsulated in `xnat_tools/dicom_export.py`

2. We run Heudiconv using ReproIn heuristic. This step is encapsulated in `xnat_tools/run_heudiconv.py`

If you'd like to run those steps separatly, you can do

```
xnat-dicom-export --user ${xnat_user}  \
--session ${session}                   \
--bids_root_dir ${bids_root_dir}
```

Followed by:

```
xnat-heudiconv --user ${xnat_user}  \
--session ${session}                \
--bids_root_dir ${bids_root_dir}
```

## Testing

For instance to run  a test file  with Peotry, run:

```
poetry run pytest -x -s -o log_cli=true --log-cli-level=INFO tests/integration/test_export_typer.py
```

`-s` makes sure that `stdout` is printed to terminal
`-o log_cli=true --log-cli-level=INFO` allows the logger output to go to cli
`-x` exists on first failure

You will need to have a local `.env` file where you set some environment variables, e.i `XNAT_PASS`

At the moment the tests can not run bids validation to do so, you can comment out the line that cleans the output directory and run the validator manually using docker.

```
bids_directory=${PWD}/tests/xnat2bids/ashenhav/study-1222/bids/
docker run -ti --rm -v ${bids_directory}:/data:ro bids/validator /data
```
