import io
import json

import requests
from requests.exceptions import HTTPError

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiYXBpX3VzZXIifQ.6aCpgPT-pg9KWbvKeX7hrrNPS4u7MVjcnCrHNwxfCps"
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


if __name__ == "__main__":

    resp = enermaps_geojson(DB_URL, 2, API_KEY)
    print(json.dumps(resp, indent=4, sort_keys=True))
