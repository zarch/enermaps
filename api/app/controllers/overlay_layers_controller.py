import io

import requests
from requests.exceptions import HTTPError

# from werkzeug.datastructures import FileStorage

# from app.models.geofile import create, list_layers

DB_URL = "http://localhost:3000"


def list_all_overlay_layers(db_url=None):
    """ Return the names + IDs of all layers in the DB
    """
    layers = [("heat", 1), ("wind", 2)]
    return layers


def get_CM_layers(layer_ids):
    """ Get a group of layers needed by a CM
    """
    pass


def enermaps_query(db_url, dataset_id, API_KEY):
    r = requests.post(
        db_url + "/rpc/enermaps_query",
        headers={"Authorization": "Bearer {}".format(API_KEY)},
        json={"dataset_id": dataset_id},
    )
    response = r.json()
    return response


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


if __name__ == "__main__":
    API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoiYXBpX2Fub24ifQ.O2tOKpbfyQSMbbVfbcHg2Nz9n_WnjneLPfcqoe4FI0o"
    resp = enermaps_query(DB_URL, 2, API_KEY)
    print(resp)


# r = requests.post('http://localhost:3000/rpc/enermaps_geojson',
# 	headers={'Authorization': 'Bearer {}'.format(API_KEY)},
# 	json={"dataset_id": 2})
# response = r.json()
# print(response)
