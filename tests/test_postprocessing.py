def test_postprocessing():
    """Integration test for bids-postprocessing executable"""
    xnat_user = "testuser"
    xnat_password  = os.getenv('XNAT_PASSWORD')
    session = "XNAT2_E00017"
    session_suffix = "01"
    bids_root_dir = "./tests/xnat2bids"

    if os.path.exists(bids_root_dir):
        shutil.rmtree(bids_root_dir, ignore_errors=True)
    
    os.mkdir(bids_root_dir)

    xnat2bids_cmd = f"xnat2bids --user {xnat_user} --password {xnat_password} \
                      --session {session} --session_suffix {session_suffix} \
                      --bids_root_dir {bids_root_dir} --seqlist 19 23 24"

    xnat2bids_split_cmd = shlex.split(xnat2bids_cmd)
    
    subprocess.run(xnat2bids_split_cmd)

    bids_dir = f"tests/xnat2bids/ashenhav/study-1222/bids"

    postprocess_cmd = f"bids-postprocess --bids_experiment_dir {bids_dir} \
                         --session {session} --session_suffix {session_suffix} \
                         --subjlist 9011 9999 111 --skipsubj 9999 111"

    postprocess_split_cmd = shlex.split(postprocess_cmd)
    
    subprocess.run(postprocess_split_cmd)

    #lazy check for the intendedFor field in one json file
    json_file = f"{bids_dir}/sub-9011/ses-01/fmap/sub-9011_ses-01_acq-greAP_phasediff.json"

    with open(json_file,'r') as f:
        data=json.load(f)
        assert data["IntendedFor"] != ""
        f.close

    #cleanup output -- for debugging coment this out
    shutil.rmtree(bids_root_dir, ignore_errors=True)