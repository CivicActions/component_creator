from flask import Flask, abort, render_template
from jinja2 import TemplateNotFound

from app.extensions import db
from app.models.components import (  # noqa: F401
    CatalogFile,
    ComponentFile,
    component_catalog,
)
from config import Config


def create_app(config_class=Config):
    app = Flask(__name__, instance_path=Config.INSTANCE_PATH)
    app.config.from_object(config_class)

    with app.app_context():
        db.init_app(app)
        db.create_all()

    from app.main import bp as bp_main

    app.register_blueprint(bp_main)

    from app.catalogs import bp as bp_catalogs

    app.register_blueprint(bp_catalogs, url_prefix="/catalogs")

    from app.components import bp as bp_components

    app.register_blueprint(bp_components, url_prefix="/components")

    @app.errorhandler(404)
    def page_not_found(error):
        try:
            return render_template("404.html"), 404
        except TemplateNotFound:
            abort(404)

    @app.errorhandler(500)
    def internal_error(error):
        return render_template("500.html"), 500

    return app
