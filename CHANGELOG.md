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
