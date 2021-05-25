export const BASE_URL = '/';
export const INITIAL_MAP_CENTER = [48.0, 7.0];
export const INITIAL_ZOOM = 5;
export const BASE_LAYER_URL =
  'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png';
export const BASE_LAYER_PARAMS= {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">'+
    'OpenStreetMap</a> &copy; <a href="https://cartodb.com/attributions">CartoDB</a>',
};

export const SELECTION_LAYERS = {
  "NUTS 0" : 0,
  "NUTS 1" : 1,
  "NUTS 2" : 2,
  "NUTS 3" : 3,
  "LAU" : 4
};

export const OVERLAY_LAYERS =
{
  "test_layer_01 " :
    {
      "display name" : "test layer 01",
      "id" : 1,
      "type" : "raster"
    },
  "test_layer_02" :
  {
    "display name" : "test layer 02",
    "id" : 2,
    "type" : "geojson"
  },
  "test_layer_03" :
  {
    "display name" : "test layer 03",
    "id" : 3,
    "type" : "vector"
  },
};
