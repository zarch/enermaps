#!/usr/bin/env python3
"""
Import the EEA dataset.
The original CSV file is downloaded and described using frictionless.
This script allows for data updates.

@author: giuseppeperonato
"""

import argparse
import json
import logging
import os
import shutil
import sys
import uuid

import frictionless
import pandas as pd
import requests
import utilities
from pandas_datapackage_reader import read_datapackage

DT = 8760
ISRASTER = False
TIME_VAR = "Year"
UNIT_VAR = "Unit"
SPATIAL_VAR = "CountryShort"
VARIABLE_VAR = "Market_Sector"
VALUE_VAR = "ValueNumeric"
DB_URL = utilities.DB_URL
REMOTE_DOWNLOAD_LOCATION = "/at_download/file"

logging.basicConfig(level=logging.INFO)


def prepare(dp: frictionless.package.Package) -> pd.DataFrame:
    """Read datapackage and prepare df using Enermaps schema."""
    data = read_datapackage(dp)
    data.columns = [str(col.strip()) for col in data.columns]  # clean column names

    enermaps_data = utilities.ENERMAPS_DF
    # Conversion
    enermaps_data["start_at"] = pd.to_datetime(data[TIME_VAR], format="%Y")
    enermaps_data["value"] = data.loc[:, VALUE_VAR].astype(float)
    enermaps_data["unit"] = data.loc[:, UNIT_VAR]
    enermaps_data["variable"] = data.loc[:, VARIABLE_VAR]
    enermaps_data["fid"] = data.loc[:, SPATIAL_VAR]
    # Constants
    enermaps_data["dt"] = DT
    enermaps_data["israster"] = ISRASTER
    # Other fields to json
    other_cols = [
        x for x in data.columns if x not in [SPATIAL_VAR, VALUE_VAR, UNIT_VAR, TIME_VAR]
    ]
    enermaps_data["fields"] = data[other_cols].to_dict(orient="records")
    enermaps_data["fields"] = enermaps_data["fields"].apply(lambda x: json.dumps(x))

    return enermaps_data


def get(url: list, dp: frictionless.package.Package, force: bool = False):
    """
    Retrieves data and check validity/update.

    Parameters
    ----------
    url : list
        URL to retrieve the data from.
        The list should composed as such: [permanent_link,remote_download_location]
    path : str
        Target path to save documents.
    dp : frictionless.package
        Datapackage agains which validating the data.
    force : Boolean, optional
        If True, new data will be uploaded even if the same as in the db. The default is False.

    Returns
    -------
    DataFrame
        Data in EnerMaps format.
    frictionless.package
        Pakage descring the data.

    """
    # Get the url redirection from the permalink
    r = requests.get(url[0], allow_redirects=True, stream=True, timeout=10)
    redirected_url = r.url
    url = redirected_url + url[1]

    # Create a unique location to store temporary data
    my_uuid = str(uuid.uuid4())

    # Download the dataset
    utilities.download_url(url, "data.zip")
    filepath = utilities.extractZip("data.zip", my_uuid)[0]
    # Rename the data, so that the path is the same regardless of the version
    os.rename(filepath, os.path.join(my_uuid, "data.csv"))

    # Inferring and completing metadata
    logging.info("Creating datapackage for input data")
    new_dp = frictionless.describe_package(
        os.path.join(my_uuid, "data.csv"), stats=True,  # Add stats
    )
    # Update the path
    new_dp.resources[0]["path"] = os.path.join(os.path.join(my_uuid, "data.csv"))
    # Add groupChar
    new_dp.resources[0].schema.get_field("ValueNumeric").group_char = ","

    # Logic for update
    if dp is not None:  # Existing dataset
        # check stats
        isChangedStats = dp["resources"][0]["stats"] != new_dp["resources"][0]["stats"]
        if "datePublished" in dp.keys():
            isChangedDate = dp["datePublished"] != new_dp["datePublished"]
        else:
            isChangedDate = False
        if (
            isChangedStats or isChangedDate
        ):  # Data integration will continue, regardless of force argument
            logging.info("Data has changed")
            if utilities.isDPvalid(dp, new_dp):
                enermaps_data = prepare(new_dp)
            else:
                return None, None
        elif force:  # Data integration will continue, even if data has not changed
            logging.info("Forced update")
            if utilities.isDPvalid(dp, new_dp):
                enermaps_data = prepare(new_dp)
            else:
                return None, None
        else:  # Data integration will stop here, returning Nones
            logging.info("Data has not changed. Use --force if you want to reupload.")
            return None, None
    else:  # New dataset
        dp = new_dp  # this is just for the sake of the schema control
        if utilities.isDPvalid(dp, new_dp):
            enermaps_data = prepare(new_dp)
        else:
            return None, None

    # Remove files
    os.remove("data.zip")
    shutil.rmtree(my_uuid)

    return enermaps_data, new_dp


if __name__ == "__main__":
    datasets = pd.read_csv("datasets.csv", engine="python", index_col=[0])
    ds_ids = datasets[datasets["di_script"] == os.path.basename(sys.argv[0])].index
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(description="Import EEA")
        parser.add_argument("--force", action="store_const", const=True, default=False)
        parser.add_argument(
            "--select_ds_ids", action="extend", nargs="+", type=int, default=[]
        )
        args = parser.parse_args()
        isForced = args.force
        if len(args.select_ds_ids) > 0:
            ds_ids = args.select_ds_ids
    else:
        isForced = False

    for ds_id in ds_ids:
        url = datasets.loc[ds_id, "di_URL"]
        dp = utilities.getDataPackage(ds_id, DB_URL)

        data, dp = get([url, REMOTE_DOWNLOAD_LOCATION], dp=dp, force=isForced)

        if isinstance(data, pd.DataFrame):
            # Remove existing dataset
            if utilities.datasetExists(ds_id, DB_URL):
                utilities.removeDataset(ds_id, DB_URL)
                print("Removed existing dataset")

            # Create dataset table
            datasets = pd.read_csv("datasets.csv", engine="python", index_col=[0])
            metadata = datasets.loc[ds_id].fillna("").to_dict()
            metadata["datapackage"] = dp
            metadata = json.dumps(metadata)
            dataset = pd.DataFrame([{"ds_id": ds_id, "metadata": metadata}])
            utilities.toPostgreSQL(dataset, DB_URL, schema="datasets")

            # Create data table
            data["ds_id"] = ds_id
            utilities.toPostgreSQL(data, DB_URL, schema="data")
