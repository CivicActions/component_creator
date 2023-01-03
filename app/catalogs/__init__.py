from flask import Blueprint

bp = Blueprint("catalogs", __name__)

from app.catalogs import routes  # noqa: E402, F401
