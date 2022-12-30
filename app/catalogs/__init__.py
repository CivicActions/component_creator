from flask import Blueprint

bp = Blueprint(
    "catalogs",
    __name__,
    template_folder="templates",
)

from app.catalogs import routes  # noqa: E402, F401
