#!/usr/bin/env python3
"""
Import the Hotmaps rasters.
The original datapackage is used to retrieve the data.
This script allows for data updates.

@author: giuseppeperonato
"""

import json
import logging
import os
import shutil
import sys
import uuid

import frictionless
import pandas as pd
import utilities

# Constants
logging.basicConfig(level=logging.INFO)
Z = None
DT = 8760
UUID = (uuid.uuid4(),)
DB_URL = utilities.DB_URL


LEGENDS = {
    "Climate zones": {
        "vis_id": UUID,
        "legend": {
            "name": "Climate zones",
            "type": "custom",
            "symbology": [
                {
                    "red": 230,
                    "green": 216,
                    "blue": 207,
                    "opacity": 1.0,
                    "value": "1",
                    "label": "Warmer climate",
                },
                {
                    "red": 242,
                    "green": 242,
                    "blue": 242,
                    "opacity": 1.0,
                    "value": "2",
                    "label": "Average climate",
                },
                {
                    "red": 157,
                    "green": 185,
                    "blue": 204,
                    "opacity": 1.0,
                    "value": "10",
                    "label": "Colder climate",
                },
            ],
        },
    }
}


# Settings for the query metadata
# these are the fields that are used to construct a query
QUERY_FIELDS = None
# empty list means all; None means do not use query fields.
# these are parameters that added to those automatically generated by the pipeline
QUERY_PARAMETERS = {"is_tiled": False, "is_raster": True}


def get(repository: str, dp: frictionless.package.Package, isForced: bool = False):
    """
    Retrieve (meta)data and check whether an update is necessary.

    Parameters
    ----------
    repository : str
        URL of the Gitlab repository (raw).
    dp : frictionless.package.Package
        Existing dp or None.
    isForced : bool, optional
        isForced update. The default is False.

    Returns
    -------
    data_enermaps : DataFrame
        df in EnerMaps format.
    dp : frictionless.package.Package
        Datapackage corresponding to the data.

    """
    new_dp = frictionless.Package(repository + "datapackage.json")
    isChangedStats = False  # initialize check

    # Prepare df containing paths to rasters
    rasters = []
    for resource_idx in range(len(new_dp["resources"])):
        if new_dp["resources"][resource_idx]["title"] == "Climate zones":
            if "temporal" in new_dp["resources"][resource_idx]:
                start_at = pd.to_datetime(
                    new_dp["resources"][resource_idx]["temporal"]["start"]
                )
            else:
                start_at = None

            if "unit" in new_dp["resources"][resource_idx]:
                unit = new_dp["resources"][resource_idx]["unit"]
            else:
                unit = None

            if new_dp["resources"][resource_idx]["format"] == "tif":
                logging.info(new_dp["resources"][resource_idx]["path"])
                utilities.download_url(
                    repository + new_dp["resources"][resource_idx]["path"],
                    os.path.basename(new_dp["resources"][resource_idx]["path"]),
                )
                raster = {
                    "value": os.path.basename(
                        new_dp["resources"][resource_idx]["path"]
                    ),
                    "variable": new_dp["resources"][resource_idx]["title"],
                    "start_at": start_at,
                    "z": Z,
                    "unit": unit,
                    "dt": DT,
                }
                rasters.append(raster)
                # check statistics for each resource
                if dp is not None and "stats" in new_dp["resources"][resource_idx]:
                    if (
                        dp["resources"][resource_idx]["stats"]
                        != new_dp["resources"][resource_idx]["stats"]
                    ):
                        isChangedStats = True
    rasters = pd.DataFrame(rasters)

    if dp is not None:  # Existing dataset
        # check stats
        isChangedVersion = dp["version"] != new_dp["version"]
        if isChangedStats or isChangedVersion:
            logging.info("Data has changed")
            data_enermaps = utilities.prepareRaster(rasters, delete_orig=True)
        elif isForced:
            logging.info("Forced update")
            data_enermaps = utilities.prepareRaster(rasters, delete_orig=True)
        else:
            logging.info("Data has not changed. Use --force if you want to reupload.")
            return None, None
    else:  # New dataset
        data_enermaps = utilities.prepareRaster(rasters, delete_orig=True)

    # Move rasters into the data directory
    if not os.path.exists("data"):
        os.mkdir("data")
    if not os.path.exists(os.path.join("data", str(ds_id))):
        os.mkdir(os.path.join("data", str(ds_id)))
    for i, row in data_enermaps.iterrows():
        shutil.move(row.fid, os.path.join("data", str(ds_id), row.fid))

    return data_enermaps, new_dp


def addLegend(data: pd.DataFrame, legends: dict):
    """Add legend for assigned variables."""
    for variable in legends.keys():
        data.loc[data["variable"] == variable, "vis_id"] = legends[variable]["vis_id"]
    return data


if __name__ == "__main__":
    datasets = pd.read_csv("datasets.csv", index_col=[0])
    script_name = os.path.basename(sys.argv[0])
    ds_ids, isForced = utilities.parser(script_name, datasets)

    for ds_id in ds_ids:
        logging.info("Retrieving Dataset {}".format(ds_id))
        dp = utilities.getDataPackage(
            ds_id,
            DB_URL,
        )

        data, dp = get(datasets.loc[ds_id, "di_URL"], dp, isForced)

        if isinstance(data, pd.DataFrame):
            if utilities.datasetExists(
                ds_id,
                DB_URL,
            ):
                utilities.removeDataset(ds_id, DB_URL)
                logging.info("Removed existing dataset")

            # Create dataset table
            metadata = datasets.loc[ds_id].fillna("").to_dict()
            metadata["datapackage"] = dp
            # Add parameters as metadata
            (
                metadata["parameters"],
                metadata["default_parameters"],
            ) = utilities.get_query_metadata(data, QUERY_FIELDS, QUERY_PARAMETERS)
            metadata = json.dumps(metadata)
            dataset = pd.DataFrame([{"ds_id": ds_id, "metadata": metadata}])
            utilities.toPostgreSQL(
                dataset,
                DB_URL,
                schema="datasets",
            )

            # Add legends
            legends = []
            for key in LEGENDS.keys():
                df = pd.DataFrame()
                df["vis_id"] = LEGENDS[key]["vis_id"]
                df["legend"] = json.dumps(LEGENDS[key]["legend"])
                legends.append(df)
            legends_df = pd.concat(legends)
            utilities.toPostgreSQL(
                legends_df,
                DB_URL,
                schema="visualization",
            )

            # Create data table
            data["ds_id"] = ds_id
            data = addLegend(data, LEGENDS)
            utilities.toPostgreSQL(
                data,
                DB_URL,
                schema="data",
            )

            # Create empty spatial table
            spatial = pd.DataFrame()
            spatial[["fid", "ds_id"]] = data[["fid", "ds_id"]]
            utilities.toPostgreSQL(
                spatial,
                DB_URL,
                schema="spatial",
            )
