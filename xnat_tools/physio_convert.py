import glob
import json
import os
import xml.etree.ElementTree as ET
from zlib import MAX_WBITS, decompressobj

import numpy as np
import pandas as pd
import typer
from pydicom import dcmread

from xnat_tools.bids_utils import prepare_path_prefixes

app = typer.Typer()


def check_xmlfile(tree):
    # for anything missing, return an empty list and it will make an empty DataFrame
    # which should work with logic below to not be written out
    images = []
    triggers = []
    puls = []
    resp = []  # start null
    for elem in tree:
        if elem.tag == "VolumeAcquisitionDescription":
            images = elem
        elif elem.tag == "PhysioTriggers":
            triggers = elem
        elif elem.attrib["TYPE"] == "PULS":
            puls = elem
        elif elem.attrib["TYPE"] == "RESP":
            resp = elem
        elif "ECG" in elem.attrib["TYPE"]:
            print("found ECG data")
        else:
            raise Exception("something new in the phys file!")
    return images, triggers, puls, resp


def determine_sample_rate(df):
    vals, counts = np.unique(np.diff(df.TIME_TICS.values), return_counts=True)
    mode_value = np.argwhere(counts == np.max(counts))
    sample_rate_tics = vals[mode_value].flatten()[0]
    time_per_tic = 0.0025  # one siemens tic is equal to 2.5ms
    sample_rate_secs = sample_rate_tics * time_per_tic
    sample_rate_hz = 1 / sample_rate_secs
    return sample_rate_tics, sample_rate_hz


def incorrect_nan(df, idx):
    # if there's a value listed as nan, but the values on either side
    # are not nan and span 2048, it really should have been a 2048 and
    # the siemens software mistakenly excluded it
    return np.isnan(df.loc[idx, "DATA"]) and (
        (df.loc[idx - 1, "DATA"] < 2048 and df.loc[idx + 1, "DATA"] > 2048)
        or (df.loc[idx - 1, "DATA"] > 2048 and df.loc[idx + 1, "DATA"] < 2048)
    )


def find_matching_bold_filename(bids_func_directory, pmu_filename):
    keys = pmu_filename.split("_")
    functional_files = glob.glob(bids_func_directory + "/*_bold.nii*")
    for k in keys:
        if k == "func-bold":
            continue
        functional_files = [x for x in functional_files if k in x]

    if len(functional_files) > 1:
        raise Exception("more than one possible matching functional run!")
    elif len(functional_files) == 0:
        raise Exception("no matching functional runs!")
    physio_stub = functional_files[0].split(".")[0].replace("_bold", "")

    return physio_stub


@app.command()
def physio_convert(
    project: str = typer.Argument(..., help="XNAT's Project ID"),
    subject: str = typer.Argument(..., help="XNAT's subject ID"),
    bids_root_dir: str = typer.Argument(..., help="Root output directory for exporting files"),
    session_suffix: str = typer.Option(
        "-1",
        "-S",
        "--session-suffix",
        help="The session_suffix is initially set to -1.\
              This will signify an unspecified session_suffix and default to sess-01.\
              For multi-session studies, the session label will be pulled from XNAT",
    ),
):
    bids_root_dir = os.path.expanduser(bids_root_dir)

    # Set up working directory
    if not os.access(bids_root_dir, os.R_OK):
        raise ValueError("BIDS Root directory must exist")

    # # Paths to export source data in a BIDS friendly way
    # project, subject, session_suffix = path_string_preprocess(project, subject, session_suffix)

    pi_prefix, study_prefix, subject_prefix, session_prefix = prepare_path_prefixes(
        project, subject, session_suffix
    )

    export_dir = f"{bids_root_dir}/{pi_prefix}/{study_prefix}/xnat-export"
    bids_func_dir = (
        f"{bids_root_dir}/{pi_prefix}/{study_prefix}/bids/{subject_prefix}/{session_prefix}/func/"
    )
    dicom_dir_template = f"{export_dir}/{subject_prefix}/{session_prefix}"
    pmu_dirs = glob.glob(f"{dicom_dir_template}/*PMU")

    if len(pmu_dirs) == 0:
        return 0

    else:
        print(f"Found {len(pmu_dirs)} physio files. Converting to BIDS.")
        for pmudir in pmu_dirs:
            os.chdir(pmudir)
            pmu_dicoms = glob.glob(f"{pmudir}/*.dcm")
            if len(pmu_dicoms) > 1:
                raise ValueError("More than one DICOM file in single PMU folder")

            physio_prefix = find_matching_bold_filename(bids_func_dir, pmudir.split("/")[-1][:-4])

            # read in dicom and save out a .xml
            pmudicom = dcmread(pmu_dicoms[0])
            pmucomp = pmudicom[0x7FE1, 0x1010].value
            cnksz = min(1024, len(pmucomp))
            decmps = []
            dcmpoj = decompressobj(16 + MAX_WBITS)

            for srtidx in range(0, len(pmucomp), cnksz):
                decmps.append(dcmpoj.decompress(pmucomp[srtidx : srtidx + cnksz]).decode("ascii"))

            # do this before check because of chuncks
            full_file_string = "".join(decmps)
            # check for unhelpful end token
            if full_file_string[-2:] != "\n\x00":
                raise Exception("missing end token?")

            pmuxml = full_file_string[:-2]
            xmlfile = pmudir.split("/")[-1] + ".xml"
            xmlfo = open(xmlfile, "w")
            xmlfo.write(pmuxml)
            xmlfo.close()

            # convert .xml to .logs
            root = ET.parse(xmlfile).getroot()
            images, triggers, puls, resp = check_xmlfile(
                list(iter(root))
            )  # check for missing/extra data
            sll = []
            pdata = []
            rdata = []

            for vol in images:  # AcqInfo: volume and slice tics.
                for slice in vol:
                    dct = slice.attrib
                    dct["Volume_ID"] = vol.attrib["ID"]
                    sll.append(dct)
            sldf = pd.DataFrame(sll).astype("int64")
            sldf = sldf.rename(columns={"ID": "Slice_ID", "ACQUISITION_TIME_TICS": "AcqTime_Tics"})
            sldf = sldf.reindex(columns=["Volume_ID", "Slice_ID", "AcqTime_Tics"])
            inittic = sldf.loc[(sldf.Volume_ID == 0) & (sldf.Slice_ID == 0), "AcqTime_Tics"].values[
                0
            ]
            secondtic = sldf.loc[
                (sldf.Volume_ID == 1) & (sldf.Slice_ID == 0), "AcqTime_Tics"
            ].values[0]
            tics_per_vol = secondtic - inittic
            numvols = max(sldf.Volume_ID)
            finaltic = (
                sldf.loc[(sldf.Volume_ID == numvols) & (sldf.Slice_ID == 0), "AcqTime_Tics"].values[
                    0
                ]
                + tics_per_vol
            )

            # ********* PULS *********
            for p in puls:
                # we only want to keep physio data within the time range of the functional data
                if int(p.attrib["TIME_TICS"]) >= inittic and int(p.attrib["TIME_TICS"]) < finaltic:
                    pdata.append(p.attrib)
            pdf = pd.DataFrame(pdata).astype("int64")

            if len(pdf) > 1:  # otherwise dont want to write this out
                pdf_sample_rate_tics, pdf_sample_rate_hz = determine_sample_rate(pdf)

                # reindex so that any missing time points are inserted with a value of nan
                pdf = (
                    pdf.set_index("TIME_TICS")
                    .reindex(
                        index=np.arange(
                            min(pdf.TIME_TICS),
                            max(pdf.TIME_TICS) + pdf_sample_rate_tics,
                            pdf_sample_rate_tics,
                        )
                    )
                    .reset_index()
                    .copy()
                )

                # time points that should have had a value of 2048 are not saved by Siemens at all,
                # so find them and fix them
                for idx in range(1, len(pdf)):
                    if incorrect_nan(pdf, idx):
                        pdf.loc[idx, "DATA"] = 2048

                # Json data to be written
                pulse_dictionary = {
                    "SamplingFrequency": pdf_sample_rate_hz,
                    "StartTime": 0,
                    "Columns": ["cardiac"],
                    "Manufacturer": "Siemens",
                    "cardiac": {"Description": "continuous pulse measurement", "Units": "mV"},
                }

                # Serializing json
                json_object = json.dumps(pulse_dictionary, indent="\t")

                # Writing to .json
                with open(physio_prefix + "_recording-cardiac_physio.json", "w") as outfile:
                    outfile.write(json_object)

                # Write pulse measurements to .tsv.gz file with matching filename
                compression_opts = dict(method="gzip")
                pdf_filename = physio_prefix + "_recording-cardiac_physio.tsv.gz"
                pdf.to_csv(
                    pdf_filename,
                    sep="\t",
                    columns=["DATA"],
                    index=False,
                    header=False,
                    compression=compression_opts,
                )

            # ********* RESP *********
            for r in resp:
                # we only want to keep physio data within the time range of the functional data
                if int(r.attrib["TIME_TICS"]) >= inittic and int(r.attrib["TIME_TICS"]) < finaltic:
                    rdata.append(r.attrib)
            rdf = pd.DataFrame(rdata).astype("int64")

            if len(rdf) > 1:  # otherwise dont want to write this out
                rdf_sample_rate_tics, rdf_sample_rate_hz = determine_sample_rate(rdf)

                # reindex so that any missing time points are inserted with a value of nan
                rdf = (
                    rdf.set_index("TIME_TICS")
                    .reindex(
                        index=np.arange(
                            min(rdf.TIME_TICS),
                            max(rdf.TIME_TICS) + rdf_sample_rate_tics,
                            rdf_sample_rate_tics,
                        )
                    )
                    .reset_index()
                    .copy()
                )

                # time points that should have had a value of 2048 are not saved by Siemens at all,
                # so find them and fix them
                for idx in range(1, len(rdf)):
                    if incorrect_nan(rdf, idx):
                        rdf.loc[idx, "DATA"] = 2048

                # json data to be written
                resp_dictionary = {
                    "SamplingFrequency": rdf_sample_rate_hz,
                    "StartTime": 0,
                    "Columns": ["respiratory"],
                    "Manufacturer": "Siemens",
                    "respiratory": {
                        "Description": "continuous respiration measurement",
                        "Units": "mV",
                    },
                }

                # Serializing json
                json_object = json.dumps(resp_dictionary, indent="\t")

                # Writing to .json
                with open(physio_prefix + "_recording-respiratory_physio.json", "w") as outfile:
                    outfile.write(json_object)

                # Write pulse measurements to .tsv.gz file with matching filename
                compression_opts = dict(method="gzip")
                rdf_filename = physio_prefix + "_recording-respiratory_physio.tsv.gz"
                rdf.to_csv(
                    rdf_filename,
                    sep="\t",
                    columns=["DATA"],
                    index=False,
                    header=False,
                    compression=compression_opts,
                )

        return 0


def main():
    app()
