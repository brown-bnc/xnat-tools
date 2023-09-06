## v1.5.0 (2023-09-06)

### Feat

- check if eeg data exported before conversion
- **bids_utils.py**: eeg bids data assigned to bids experiment directory
- run_mne_eeg2bids function to convert brainvision data to bids standard
- export session level resources, specifically for eeg data
- add part-mag and -phase to BIDS names
- **xnat_utils.py**: include sequence by name
- **xnat_utils.py**: allow sequences to be skipped by name

### Fix

- **bids_utils.py**: make default task for eeg data todo
- **bids_utils.py**: update download resources to handle non-absolute bids experiment paths
- changes type of skip / include list to str

### Refactor

- **bids_utils.py**: refactor request string and add resource name to logging
- **xnat_utils.py**: deleting unused function

## v1.4.1 (2023-08-16)

## v1.4.0 (2023-07-11)

### Feat

- integrate BIDS conversion of physio data

## v1.3.0 (2023-06-15)

### Feat

- **installation.md**: update docs with feat change type to trigger bump version action

### Fix

- **installation.md**: fix tags url

## v1.2.2 (2023-06-14)

## v1.2.1 (2023-05-15)

### Fix

- **bids_utils.py**: add exist_ok param to makedirs

## v1.2.0 (2023-05-12)

### Feat

- **xnat2bids.py**: add modular function dcm2bids for bids conversion pipeline

### Fix

- **dicom_export**: add exist_ok to makedirs to resolve synchronization issue
- add path preprocessing for project and subject data
- check bids_experiment_dir path in github runner
- fetch project and subject data when running with --skip-export

### Refactor

- **pyproject.toml**: remove xnat-dicom-export, xnat-heudiconv, bids_postprocess, and xnat-dcm2bids from pyproject

## v1.1.1 (2023-04-06)

### Fix

- **xnat2bids.py**: provide correct path for bids experiment directory

## v1.1.0 (2023-04-05)

### Feat

- support physio data export
- **test_xnat_utils.py**: update unit tests to check get_project_subject_session function for multisession data

### Fix

- check if fmap folder exists before bids_postprocess
- remove redundant resourcesURL specification
- limit filesURL to DICOM format files
- test_bids_utils includes label field
- update bids_postprocess to support single or multiple session selection for IntendedFor mapping, implement overwrite flag, and incorporate into xnat2bids pipeline

### Refactor

- refactor test utility function and documentation
- update bids postprocessing to suppost skipping one or multiple sessions

## v1.0.10 (2022-11-30)

### Fix

- update dev docs
- update handling session data
- **pre-commit-config.yaml**: update flake8 location
- **pre-commit.yml**: update pre-commit action to v3
- extract session suffix from session label for heudiconv

## v1.0.9 (2022-10-27)

### Fix

- **bids_utils.py**: resolve v1_0_8 release bids post-processing bug

## v1.0.8 (2022-10-18)

### Fix

- correct processing and update numpy
- insert intendedfor scans into fieldmap and handle sbref protocol name
- manual update of xnat-tools version for poetry
- populate IntendedFor field map object array, resolve protocol naming for sbref derivative
- remove SBREF derivative string matching, now being handled in heudiconv

## v1.0.6 (2021-11-02)

### Fix

- add missing field map derivatives

## v1.0.5 (2021-05-21)

### Fix

- update to use new xnat host

## v1.0.4 (2021-01-24)

## v2.0.0 (2021-01-23)

### Fix

- revert failed versions
- fixing publish workflow
- make inputs for postprocess CLI consistent with variable names

## v1.0.3 (2021-01-14)

### Fix

- add and abstract string preprojecissing of proj, sub, sess

## v1.0.2 (2020-11-23)

### Fix

- remove other heudiconv directories that messup overwrite
- remove other heudiconv directories that messup overwrite
- add blank space before heudiconv's overwrite flag
- add blank space before heudiconv's overwrite flag

## v1.0.1 (2020-11-17)

### Perf

- capture duplicate warnings

### Fix

- **overwrite**: don't ignore errors, and pass flag to heudiconv
- bring back saving the file after setting DICOM header

## v1.0.0 (2020-10-22)

### Refactor

- Merge pull request #47 from brown-bnc/feat/add-documentation
- --verbose and --very verbose for postprocess
- change the format of CLI inputs to be consistent to unix style
- put dicom-expoert and run-heudiconv back in separate files
- **dicom_export**: clomplete options/inputs and run through
- **WIP**: add dicom_export to xnat2bids_typer
- **WIP**: start skeleton for typer cli for xnat2bids

### BREAKING CHANGE

- Changes the CLI to use typer, adds MkDocs, pre-commit hooks and Github Actions

### Fix

- bring back lost build-system from pyproject file
- get xnat2bids and tests back working
- adjust sintax for commands in separate files

### Feat

- transition posprocessing to typer

## v0.1.7 (2020-07-06)

### Fix

- **tests**: add full path and make sequences strings
- **tests**: add misssing imports
- fixes to logging, seriesDescList indexing and dicom extension (.IMA)

### Feat

- WIP working on overwrite behavior
- add identifier to logfiles
- check dicom extension, add formatting

## v0.1.6 (2020-05-28)

### Fix

- put back the poetry.lock, didn't know it was needed for the docker build
- add session to the path of IntendedFor nii file

## v0.1.5 (2020-05-22)

## v0.1.4 (2020-05-19)

## v0.1.3 (2020-04-08)

### Feat

- Add files and functions to insert `IntendedFor` field
- add --session_suffix as a required input

## v0.1.2 (2020-03-09)

### Fix

- coloredlogs respect logging level

### Feat

- add minimal test to have the ability of making sure things don't break
- add --skilist to arguments

## v0.1.1 (2020-03-06)

### Fix

- We are now using SSL!

## v0.1.0 (2020-02-28)

### Fix

- enter password only once for xnat2bids

## v0.1.0-beta (2020-02-26)

### Fix

- remove heudiconv extras
- make host optional to use default value
- remove bid_validator, fix empty log, parse only know args
- bidsmap now works properly. Add missing arguments
- names are no longer converted to lower-case

### Feat

- add color to logging
- ask for password, add logging, add sequence list

## 0.1.0-alpha (2020-02-18)

### Fix

- remove selected list
- change dicom tags to match bidsname for protocol and series description
- miscelaneous typo/type errors
- use argument bidsmap json file, take logs out of bids directory
- replace undescores for dashes in session and subject labels
- add xnat_tools to module imports
- user variable for bids_root_dir instead of hardcoded path
- add package prefix to imports

### Feat

- detect multiple runs
- handle aascout planes and mprage rms
- add xnat2bids code
- bring in xnat2bids code from plugin
