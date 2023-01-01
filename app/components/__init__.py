from flask import Blueprint

bp = Blueprint("components", __name__)

from app.components import routes  # noqa: E402, F401
