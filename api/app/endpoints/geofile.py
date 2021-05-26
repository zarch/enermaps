"""Endpoint for the manipulation of geofiles
"""
from flask import redirect, send_file, url_for
from flask_restx import Namespace, Resource, abort
from werkzeug.datastructures import FileStorage

from app.models import geofile as geofile

api = Namespace("geofile", description="Data management related endpoints")


upload_parser = api.parser()
upload_parser.add_argument("file", location="files", type=FileStorage, required=True)


@api.route("/")
class GeoFiles(Resource):
    """Listing and creation of raster/shapefile"""

    def get(self):
        """Return a list of all geofile known by
        the system and accessible by the user making the request."""
        layers = geofile.list_layers()
        return {layer.name: layer.as_dict() for layer in layers}

    @api.expect(upload_parser)
    def post(self):
        """Add a geofile, currently only raster is supported in a geotiff format.

        Later we plan on supporting
        * csv: linking a NUTS to a value and shapefile.
        """
        args = upload_parser.parse_args()
        uploaded_file = args["file"]  # This is FileStorage instance
        # TODO this should be in the error handler instead
        try:
            layer = geofile.create(uploaded_file)
        except geofile.SaveException as e:
            abort(400, str(e))
        if not layer.projection:
            layer.delete()
            abort(400, "The uploaded file didn't contain a projection")
        return redirect(url_for(".geofile_geo_files"))


@api.route("/<string:layer_id>")
class GeoFile(Resource):
    def get(self, layer_id):
        """Get a geofile, currently shapefile as zip
        and raster as geotiff is supported."""
        print("get " + str(layer_id))

        layer = geofile.load(layer_id)
        layer_fd, mimetype = layer.as_fd()
        # Send the contents of a file to the client.
        # The first argument can be a file path or a file-like object.
        # Paths are preferred in most cases because Werkzeug can manage
        # the file and get extra information from the path. Passing a file-like
        # object requires that the file is opened in binary mode, and is mostly
        # useful when building a file in memory with io.BytesIO.
        return send_file(layer_fd, mimetype=mimetype)

    def delete(self, layer_id):
        """Remove a geofile by id."""
        geofile.load(layer_id).delete()
        return redirect(url_for(".geofile_geo_files"))
