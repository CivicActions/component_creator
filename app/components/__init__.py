from flask import Blueprint

bp = Blueprint(
    "components",
    __name__,
    template_folder="templates",
)

from app.components import routes  # noqa: E402, F401
