# XNAT Tools

XNAT tools maintained by the Behavioral Neuroimaging Center for the Brown University MRI users

## XNAT2BIDS
This python package provides scripts that facilitates exporting data from XNAT to BIDS format.

### Installation 

#### Using Docker

```
docker pull docker pull brownbnc/xnat_tools:<version>
```

*Version:*
* `latest`: Is the build of master
* `vX.X.X`: Latest tagged stable release

You can confirm the tags [here](https://hub.docker.com/repository/docker/brownbnc/xnat_tools/tags?page=1)

#### Using pipx

If you are using this package in a stand-alone fashion, and you don't want to use Docker, we recommend using [pipx](https://github.com/pipxproject/pipx). Please check their README for installation instructions. Once `pipx` is installed you can run

```
pipx install git+https://github.com/brown-bnc/xnat-tools/archive/v0.1.0-beta.zip
```

```
pipx install git+https://github.com/brown-bnc/xnat-tools.git
```

### Prerequisites:

We first need to install the dcm2niix . This is a dependency of Heudiconv, that doesn't get installed by Heudiconv itself

```
brew install dcm2niix
```





### Running via poetry
```
poetry run xnat2bids --session XNAT_DEV_E00009 --host http://bnc.brown.edu/xnat-dev --user <user> --pass <password> --bids_root_dir "~/data/bids-export"
```

The command performs thevfollowing steps:

1. Export to a heudiconv friendly directory structure. We follow the structure sugegsted by [this ReproIn guide](https://github.com/ReproNim/reproin), enabling us to use their heuristic. Also, note that the given command exports to path /data/xnat/bids-export. We mount this path to our XNAT instance. This step is encapsulated in `src/dicom_export.py`
2. We run Heudiconv using ReproIn heuristic. This step is encapsulated in `src/run_heudiconv.py`

If you'd like to run those steps separatly, you can do 

```
poetry run xnat-dicom-export --session XNAT_DEV_E00009 --host http://bnc.brown.edu/xnat-dev --user <user> --pass <password> --bids_root_dir "~/data/bids-export"
```

```
poetry run xnat-heudiconv --session XNAT_DEV_E00009 --host http://bnc.brown.edu/xnat-dev --user <user> --pass <password> --bids_root_dir "~/data/bids-export"
```

## Testing in remote ( Developers)

In remote

### Checkout source
```
cd maintain/src
git clone https://github.com/brown-bnc/xnat-docker-plugins.git
```

### Pull docker 

```
docker pull brownbnc/xnat2bids-heudiconv:v0.1.0
```

### Run with source and needed volumes
```
docker run --rm -it --entrypoint /bin/bash  \
           -v /maintain/src/xnat-docker-plugins/xnat2bids-heudiconv/:/opt/src/bids/ \
           -v /mnt/brownresearch/xnat-dev/bids-export/:/data/xnat/bids-export \
           --name xnat2bids-heudiconv brownbnc/xnat2bids-heudiconv:v0.1.0 

```
### Run without local source
```
docker run --rm -it --entrypoint /bin/bash \
           -v /mnt/brownresearch/xnat-dev/bids-export/:/data/xnat/bids-export \
           --name xnat2bids-heudiconv brownbnc/xnat2bids-heudiconv:v0.1.0 

```

```
docker run --rm -it --entrypoint /bin/bash \
           -v /Users/mrestrep/data/bids-export/:/data/xnat/bids-export \
           --name xnat2bids-heudiconv brownbnc/xnat2bids-heudiconv:v0.1.0 

```

### Using singularity

```
singularity build xnat2bids-heudiconv-v0.1.0.simg docker://brownbnc/xnat2bids-heudiconv:v0.1.0

singularity shell -B /users/mrestrep/data/mrestrep/bids-export/:/data/xnat/bids-export xnat2bids-heudiconv-v0.1.0.simg

```


### Run scripts

#### Export dicoms
```
python dicom_export.py --host http://bnc.brown.edu/xnat-dev --user <user> --password <pass> --subject BIDSTEST --session XNAT_DEV_E00009 --project SANES_SADLUM --bids_root_dir "/data/xnat-dev/bids-export"
```
#### Convert to BIDS using Heudiconv

```
python run_heudiconv.py --host http://bnc.brown.edu/xnat-dev --user <user> --password <pass> --subject BIDSTEST --session XNAT_DEV_E00009 --project SANES_SADLUM --bids_root_dir "/data/xnat/bids-export"
```

##### Direct call to Heudiconv from inside container
If need to test Heudiconv directly we can do:

<!-- heudiconv -f reproin --bids -o /data/xnat-dev/bids-export/sanes/study-sadlum/rawdata/sub-bidstest/ses-xnat_dev_e00009 --files /data/xnat-dev/bids-export/sanes/study-sadlum/sourcedata/sub-bidstest/ses-xnat_dev_e00009 -c none -->

```
heudiconv -f reproin --bids -o /data/xnat/bids-export/sanes/study-sadlum/rawdata/ --dicom_dir_template /data/xnat/bids-export/sanes/study-sadlum/sourcedata/sub-{subject}/ses-{session}/*/*.dcm --subjects bidstest --ses xnat_dev_e00009
```