var map = L.map("map").setView([51.505, -0.09], 13);

var base0 = L.tileLayer.wms("http://ows.mundialis.de/services/service?", {
  layers: "TOPO-OSM-WMS",
});
map.addLayer(base0);
var base_map = {};
const workspace_name = "enermaps";
const layer_name = "nuts";
for (var nuts_index = 0; nuts_index < 4; nuts_index++) {
  base_map[layer_name.toUpperCase() + " " + nuts_index] = L.tileLayer.nutsLayer(
    "http://127.0.0.1:2000/geoserver/" + workspace_name + "/wms?",
    {
      transparent: "true",
      layers: "enermaps:nuts",
      format: "image/png",
      cql_filter: "stat_levl_ =" + nuts_index + " AND year='2013-01-01'",
    }
  );
}
base_map["LAU"] = L.tileLayer.nutsLayer(
  "http://127.0.0.1:2000/geoserver/enermaps/wms?",
  {
    transparent: "true",
    layers: "enermaps:tbl_lau1_2",
    format: "image/png",
  }
);

var drawingLayer = new L.DrawingLayer();
//map.addLayer(editableLayers);
base_map["Draw"] = drawingLayer;
layer_control = L.control.layers(base_map, {})
layer_control.addTo(map);
$.ajax({
	url: "/api/geofile"
}).done(function(data){
console.log("layers are :", data.files);
for (const layer_index in data.files) {
  const layer_name = data.files[layer_index];
  const layer = L.tileLayer.wms(
    "/api/wms?",
    {
      transparent: "true",
      layers: layer_name,
      format: "image/png",
    }
  );
  layer.is_overlay = true;
  layer_control.addOverlay(layer, layer_name);
	console.log("adding ", layer);
}
});

map.addControl(
  new L.Control.Search({
    url: "https://nominatim.openstreetmap.org/search?format=json&q={s}",
    jsonpParam: "json_callback",
    propertyName: "display_name",
    propertyLoc: ["lat", "lon"],
    marker: false,//L.circleMarker([0, 0], { radius: 30 }),
    autoCollapse: true,
    autoType: false,
    minLength: 2,
  })
);

$.ajax({
  url: "/api/cm/0/task/0",
  success: function( result ) {
      var ctx = document.getElementById('myChart').getContext('2d');
      var myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Red', 'Blue', 'Yellow', 'Green', 'Purple', 'Orange'],
            datasets: [{
                label: '# of Votes',
                data: [12, 19, 3, 5, 2, 3],
                backgroundColor: [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(255, 159, 64, 0.2)'],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)'],
                borderWidth: 1}]
            }})
  }});




//map.on('draw:created', function(e) {
//  var type = e.layerType,
//    layer = e.layer;
//
//  if (type === 'marker') {
//    layer.bindPopup('A popup!');
//  }
//
//  editableLayers.addLayer(layer);
//});
