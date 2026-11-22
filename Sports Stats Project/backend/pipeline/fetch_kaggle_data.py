import sys
import os

# expanding scope of current directory to find files
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import kaggle
import json
from pipeline.utils import DATA_DIR

tracker = os.path.join(os.path.dirname(__file__), "..", "kaggle_version.json")

def fetch_kaggle_data():
    print("Authenticating kaggle api...")
    kaggle.api.authenticate()

    datasets = kaggle.api.dataset_list(search='historical-nba-data-and-player-box-scores')
    match = [dataset for dataset in datasets if dataset.ref == "eoinamoore/historical-nba-data-and-player-box-scores"][0]

    current_version = match.current_version_number

    if (os.path.exists(tracker)):
        with open(tracker, "r") as f:
            saved_data = json.load(f)
        stored_value = saved_data["kaggle_version"]
    else:
        stored_value = None
    
    if (current_version == stored_value):
        print("Dataset is up to date!")
        return None

    # download the new CSVs, but DON'T save the version yet —
    # we only save it once the database load fully succeeds (see save_kaggle_version)
    kaggle.api.dataset_download_files(match.ref, path=DATA_DIR, unzip=True)
    return current_version

# called only after load_all() finishes without crashing.
# if the load crashes, this never runs, so the next run sees the old version and retries.
def save_kaggle_version(version):
    with open(tracker, "w") as f:
        json.dump({"kaggle_version": version}, f)

if __name__ == "__main__":
    fetch_kaggle_data()