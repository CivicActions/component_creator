from pathlib import Path

from flask import abort, current_app, flash, redirect, render_template, request, url_for
from jinja2 import TemplateNotFound
from werkzeug.utils import secure_filename

from app.catalogs import bp
from app.catalogs.forms import CatalogForm, UpdateCatalogForm
from app.extensions import db
from app.models.components import Catalog
from app.oscal.catalog import CatalogModel
from app.oscal.oscal import BackMatter

ALLOWED_EXTENSIONS = {"json"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_control_links(links: list, backmatter: BackMatter) -> dict:
    links_list: dict = {
        "reference": [],
        "related": [],
    }

    for link in links:  # type: ignore
        rel = link.rel
        href = link.href[1:]
        if rel == "reference":
            resource = backmatter.get_resource_by_uuid(href)
            links_list["reference"].append(resource)
        elif rel == "related":
            links_list["related"].append(href)
    return links_list


def replace_odps(statements: list, parameters: dict) -> list:
    for k, s in enumerate(statements):
        text = s.get("prose")
        for key, value in parameters.items():
            placeholder = "{{ insert: param, " + key + " }}"
            text = text.replace(placeholder, value)
        statements[k]["prose"] = text
    return statements


@bp.route("/")
def catalogs_list():
    catalogs = Catalog.query.all()

    if not catalogs:
        flash(
            message="There are no Catalogs installed. Click the link below to add one.",
            category="message",
        )

    try:
        return render_template("catalogs.html", catalogs=catalogs)
    except TemplateNotFound:
        abort(404)


@bp.route("/add", methods=["GET", "POST"])
def catalog_add():
    form = CatalogForm()
    if request.method == "POST":
        error = None
        if form.validate_on_submit():
            title = request.form["name"]
            description = request.form["description"]
            file = request.files["catalog_file"]
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                upload_directory = Path(current_app.config["UPLOAD_FOLDER"]).joinpath(
                    "catalogs"
                )
                if not upload_directory.is_dir():
                    upload_directory.mkdir(parents=True, exist_ok=False)
                filepath = upload_directory.joinpath(filename).as_posix()
                request.files["catalog_file"].save(filepath)
                try:
                    catalog = Catalog(
                        title=title,
                        description=description,
                        filename=filepath,
                    )
                    db.session.add(catalog)
                    db.session.commit()
                except db.SQLAlchemyError as exc:
                    error = f"Catalog {title} already exists: {exc}"
                else:
                    return redirect(
                        url_for("catalogs.catalog_view", catalog_id=catalog.id)
                    )

        flash(error)

    try:
        return render_template(
            "catalog_create_form.html", form=form, title="Add Catalog"
        )
    except TemplateNotFound:
        abort(404)


@bp.route("/<int:catalog_id>", methods=["GET"])
def catalog_view(catalog_id: int):
    catalog_data = db.session.execute(
        db.select(Catalog).filter_by(id=catalog_id)
    ).first()
    catalog = CatalogModel.from_json(catalog_data[0].filename)
    metadata = catalog.metadata
    groups = catalog.get_groups()
    return render_template(
        "catalog.html",
        metadata=metadata,
        groups=groups,
        catalog=catalog_data,
    )


@bp.route("/<int:catalog_id>/update", methods=["GET", "POST"])
def catalog_update(catalog_id: int):
    form = UpdateCatalogForm()
    catalog = db.session.execute(db.select(Catalog).filter_by(id=catalog_id)).first()

    if catalog is None:
        abort(404, f"Catalog ID {catalog_id} doesn't exist")

    if request.method == "POST":
        error = None
        if form.validate_on_submit():
            catalog.title = request.form["name"]
            catalog.description = request.form["description"]

            try:
                db.session.commit()
            except db.IntegrityError:
                error = f"Catalog {catalog_id} update failed."
            else:
                return redirect(url_for("catalogs.catalog_view", id=catalog_id))

        flash(error)

    form.name.data = catalog.title
    form.description.data = catalog.description
    return render_template(
        "catalogs/catalog_update_form.html",
        form=form,
        title="Update Catalog",
        catalog=catalog,
    )
