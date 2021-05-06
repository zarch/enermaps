import io

import requests
from requests.exceptions import HTTPError
from werkzeug.datastructures import FileStorage

from app.models.geofile import create, list_layers

DB_URL = "http://localhost:3000"


def get_NUTS(db_url, nuts_id):
    """
    """
    payload = {"id": nuts_id}

    try:
        resp = requests.get(db_url, payload)
        resp.raise_for_status()
    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as e:
        print(f"Other error occurred: {e}")
        print(f"Other error occurred: {e}")

    try:
        resp.json()
    except Exception as e:
        print("Invalid response")
        print(f"Other error occurred: {e}")


def get_LAU(db_url):
    payload = {}

    try:
        resp = requests.get(db_url, payload)
        resp.raise_for_status()
    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as e:
        print(f"Other error occurred: {e}")

    try:
        resp.json()
    except Exception as e:
        print("Invalid response")
        print(f"Other error occurred: {e}")


def init_selection_layers(db_url):

    # THESE DATASETS ARE MENDATORY
    nuts0 = get_NUTS(db_url, 0)
    nuts1 = get_NUTS(db_url, 1)
    nuts2 = get_NUTS(db_url, 2)
    nuts3 = get_NUTS(db_url, 3)
    lau = get_LAU(db_url)

    # Put datasets to local storage
    to_local_storage(nuts0, "nuts0", "application/zip")
    to_local_storage(nuts1, "nuts1", "application/zip")
    to_local_storage(nuts2, "nuts2", "application/zip")
    to_local_storage(nuts3, "nuts3", "application/zip")
    to_local_storage(lau, "lau", "application/zip")


def to_local_storage(resp_data, filename, content_type):
    # content_type is used to call the right class for storage: GeoJSONLayer,
    # VectorLayer or RasterLayer
    # Vector layers have the extention .zip or .geojson

    # Raster layers:  ["image/geotiff", "image/tiff"]
    # Vector layers: ["application/zip"]
    # Geojson layers (subclass of Vector layers): ["application/json",
    #                           "application/geojson", "application/geo+json"]
    file_upload = FileStorage(resp_data, filename, content_type=content_type)
    create(file_upload)


def get_from_db(API_KEY):
    API_KEY = {API_KEY}
    r = requests.get(
        "http://localhost:3000/datasets",
        headers={"Authorization": "Bearer {}".format(API_KEY)},
    )
    response = r.json()
    print(response)


# ==============================================================================
# Data from Hotmaps
# ==============================================================================


def fetch_dataset(base_url, get_parameters, filename, content_type):
    """Get a single zip dataset and import it into enermaps."""
    existing_layers_name = [layer.name for layer in list_layers()]
    if filename in existing_layers_name:
        print("Not fetching {}, we already have it locally".format(filename))
        return
    print("Fetching " + filename)
    with requests.get(base_url, params=get_parameters, stream=True) as resp:
        resp_data = io.BytesIO(resp.content)

    file_upload = FileStorage(resp_data, filename, content_type=content_type)
    create(file_upload)


def init_datasets():
    """If the dataset was found to be empty, initialize the datasets for
    the selection of:
    * NUTS(0|1|2|3)
    * LAU

    Currently, we fetch the dataset from hotmaps.eu
    """
    print("Ensure we have the initial set of dataset")
    base_url = "https://geoserver.hotmaps.eu/geoserver/hotmaps/ows"
    base_query_params = {
        "service": "WFS",
        "version": "1.0.0",
        "request": "GetFeature",
        "outputFormat": "SHAPE-ZIP",
    }
    nuts_query = {**base_query_params, **{"typeName": "hotmaps:nuts"}}
    cql_filter = "stat_levl_='{!s}' AND year='2013-01-01'"
    lau_query = {**base_query_params, **{"typeName": "hotmaps:tbl_lau1_2"}}
    for i in range(4):
        nuts_query["CQL_FILTER"] = cql_filter.format(i)
        filename = "nuts{!s}.zip".format(i)
        fetch_dataset(base_url, nuts_query, filename, "application/zip")

    filename = "lau.zip"
    fetch_dataset(base_url, lau_query, filename, "application/zip")

    tif_query = {
        "service": "WMS",
        "version": "1.1.0",
        "request": "GetMap",
        "layers": "hotmaps:gfa_tot_curr_density",
        "styles": "",
        "bbox": "944000.0,938000.0,6528000.0,5414000.0",
        "width": 768,
        "height": 615,
        "srs": "EPSG:3035",
        "format": "image/geotiff",
    }
    filename = "gfa_tot_curr_density.tiff"
    fetch_dataset(base_url, tif_query, filename, "image/tiff")
