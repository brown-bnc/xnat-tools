This package installs the following executables which constitute the main way that users will interface with xnat-tools

* `xnat2bids` : `xnat_tools/xnat2bids.py`
* `xnat-dicom-export`: `xnat_tools/dicom_export.py`
* `xnat-heudiconv`: `xnat_tools/run_heudiconv.py`
* `bids-postprocess`: `xnat_tools/bids_postprocess.py`

`xnat2bids` exports an XNAT experiment (or MRI session) to the BIDS format in one run. This executable under the hood is performing two operations:

1. Export to a [Heudiconv](https://github.com/nipy/heudiconv) friendly directory structure. We follow the structure suggested by the [ReproIn guide](https://github.com/ReproNim/reproin), enabling us to use their [heuristic file](https://github.com/nipy/heudiconv/blob/master/heudiconv/heuristics/reproin.py). This step is encapsulated in `xnat_tools/dicom_export.py`
2. We run Heudiconv using ReproIn heuristic. This step is encapsulated in `xnat_tools/run_heudiconv.py`

In general, users will be interacting only with `xnat2bids`. However, in cases where troubleshooting is necessary, it may be convenient to run the two steps separately. The first step, `dicom_export`,  is time consuming as all the data needs to be downloaded form the server. If the user can verify that the export looks correct, and the errors happen only when executing `run_heudiconv`, then running the two steps separately can save significant time. 

At the moment `bids-postprocess` is used to insert the `IntendedFor` field to JSON sidecart for fieldmap data.