"""Entrypoint for the application.
This contains the initial creation of dataset in dev
mode and the initialisation of the applicaton.
"""
import os

from flask import Blueprint, Flask
from flask_restx import Api

from app.controllers import overlay_layers_controller, selection_layers_controller
from app.endpoints import calculation_module, geofile, wms
from app.healthz import healthz
from app.models.geofile import create
from app.redirect import redirect_to_api


def create_app(environment="production", testing=False):
    """Create the application and set the configuration.
    By default, testing mode is set to False."""
    app = Flask(__name__)
    app.config["TESTING"] = testing
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
    app.config["MAX_PROJECTION_LENGTH"] = 1024
    app.config["UPLOAD_DIR"] = "/tmp/upload_dir"
    app.config["WMS"] = {}
    app.config["WMS"]["ALLOWED_PROJECTIONS"] = ["EPSG:3857"]
    app.config["WMS"]["MAX_SIZE"] = 2048 ** 2
    app.config["WMS"]["GETMAP"] = {}
    app.config["WMS"]["GETMAP"]["ALLOWED_OUTPUTS"] = ["image/png", "image/jpg"]
    for k, v in app.config.items():
        app.config[k] = os.environ.get(k, v)

    api_bp = Blueprint("api", "api", url_prefix="/api")

    api = Api(api_bp)
    api.add_namespace(geofile.api)
    api.add_namespace(wms.api)
    api.add_namespace(calculation_module.api)
    app.register_blueprint(api_bp)
    app.register_blueprint(redirect_to_api)
    app.register_blueprint(healthz)

    with app.app_context():
        if not app.testing:
            selection_layers_controller.init_datasets()
            # overlay_layers = layers_controller.list_all_overlay_layers()
            file_upload = overlay_layers_controller.layer_from_db()
            create(file_upload)
    return app
