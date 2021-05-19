import base64
import inspect
import io
import json
import os
import sys

import requests
from requests.exceptions import HTTPError
from werkzeug.datastructures import FileStorage

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

# from models.geofile import create


API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoiYXBpX3VzZXIifQ.i34NXwqCFDV84ZKjZ0b7r4OmHOeRkONEEKARQSbNL00"
DB_URL = "http://localhost:3000"


def list_all_overlay_layers(db_url=None):
    """ Return the names + IDs of all layers in the DB
    """
    # layers = [("heat", 1), ("wind", 2)]
    pass


def get_CM_layers(layer_ids):
    """ Get a group of layers needed by a CM
    """
    pass


def get_raster_dataset(db_url, raster_id):
    """
    Get a raster file with a given ID from the database
    Return: raster file as bytes
    """
    payload = {"id": raster_id}
    try:
        resp = requests.get(db_url, payload, stream=True)
        resp.raise_for_status()
    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as e:
        print(f"Other error occurred: {e}")

    try:
        # Response in bytes
        resp_data = io.BytesIO(resp.content)
    except Exception as e:
        print("Invalid response")
        print(f"Other error occurred: {e}")
    return resp_data


def get_vector_dataset(db_url, dataset_id):
    payload = {"id": dataset_id}

    try:
        resp = requests.get(db_url, payload)
        resp.raise_for_status()
    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as e:
        print(f"Other error occurred: {e}")

    try:
        # Decoded response - the encoding is guessed based
        # on the header
        resp.text
    except Exception as e:
        print("Error")
        print(f"Other error occurred: {e}")


def enermaps_geojson(db_url, dataset_id, API_KEY):
    url = db_url + "/rpc/enermaps_geojson"
    r = requests.post(
        url,
        headers={"Authorization": "Bearer {}".format(API_KEY)},
        json={"dataset_id": dataset_id},
    )
    return r.json()


# def fetch_dataset(base_url, get_parameters, filename, content_type):
#     """Get a single zip dataset and import it into enermaps."""
#     existing_layers_name = [layer.name for layer in list_layers()]
#     if filename in existing_layers_name:
#         print("Not fetching {}, we already have it locally".format(filename))
#         return
#     print("Fetching " + filename)
#     with requests.get(base_url, params=get_parameters, stream=True) as resp:
#         resp_data = io.BytesIO(resp.content)

#     file_upload = FileStorage(resp_data, filename, content_type=content_type)
#     create(file_upload)


if __name__ == "__main__":
    # setup(name='app', version='1.0', packages=find_packages())
    # from app.models.geofile import create

    resp = enermaps_geojson(DB_URL, 2, API_KEY)
    # print(json.dumps(resp, indent=4, sort_keys=True))
    resp = json.dumps(resp, indent=4, sort_keys=True)

    ascii_message = resp.encode("ascii")
    output_byte = base64.b64encode(ascii_message)
    # print(output_byte)

    # resp_data = None
    # with enermaps_geojson(DB_URL, 2, API_KEY) as resp:
    #     resp_data = io.BytesIO(resp.content)

    file_upload = FileStorage(output_byte, "Test", content_type="application/geo+json")
    # create(file_upload)
