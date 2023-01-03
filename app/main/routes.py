import os

from flask import current_app, render_template, send_from_directory

from app.catalogs.routes import catalog_block
from app.main import bp


@bp.route("/")
def index():
    catalogs = catalog_block()
    return render_template(
        "main/home.html",
        content="",
        catalogs=catalogs,
        components={},
    )


@bp.route("/about")
def about():
    text = "This is the About page."
    return render_template(
        "main/page.html",
        content=text,
        title="About",
    )


@bp.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(current_app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )
