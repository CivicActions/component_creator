from pathlib import Path

from flask import abort, current_app, flash, redirect, render_template, request, url_for
from jinja2 import TemplateNotFound
from werkzeug.utils import secure_filename

from app.catalogs import bp
from app.catalogs.forms import CatalogForm, UpdateCatalogForm
from app.extensions import db
from app.models.components import CatalogFile
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


def catalog_block():
    catalogs = CatalogFile.query.all()
    return catalogs


@bp.route("/")
def catalogs_list():
    catalogs = CatalogFile.query.all()

    if not catalogs:
        flash(
            message="There are no Catalogs installed. Click the link below to upload one.",
            category="message",
        )

    try:
        return render_template("catalogs/list.html", catalogs=catalogs)
    except TemplateNotFound:
        abort(404)


@bp.route("/create", methods=["GET", "POST"])
def catalog_create():
    form = CatalogForm()
    if request.method == "POST":
        error = None
        if form.validate_on_submit():
            title = form.title.data
            description = form.description.data
            source = form.source.data
            file = form.catalog_file.data
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
                    catalog = CatalogFile(
                        title=title,
                        description=description,
                        source=source,
                        filename=filepath,
                    )
                    db.session.add(catalog)
                    db.session.commit()
                except db.SQLAlchemyError as exc:
                    error = f"Catalog {title} already exists: {exc}"
                else:
                    flash(f"Catalog {title} created.", "message")
                    return redirect(
                        url_for("catalogs.catalog_view", catalog_id=catalog.id)
                    )
        flash(error)
    try:
        return render_template(
            "catalogs/create_form.html", form=form, title="Add Catalog"
        )
    except TemplateNotFound:
        abort(404)


@bp.route("/<int:catalog_id>", methods=["GET"])
def catalog_view(catalog_id: int):
    catalog_data = CatalogFile.query.get_or_404(catalog_id)
    catalog = CatalogModel.from_json(catalog_data.filename)
    metadata = catalog.metadata
    groups = catalog.get_groups()
    return render_template(
        "catalogs/catalog.html", metadata=metadata, groups=groups, catalog=catalog_data
    )


@bp.route("/<int:catalog_id>/update", methods=["GET", "POST"])
def catalog_update(catalog_id: int):
    form = UpdateCatalogForm()
    catalog = CatalogFile.query.get_or_404(catalog_id)

    if request.method == "POST":
        if form.validate_on_submit():
            catalog.title = form.title.data
            catalog.description = form.description.data
            catalog.source = form.source.data

            try:
                db.session.add(catalog)
                db.session.commit()
            except db.IntegrityError:
                flash(f"Catalog {catalog_id} update failed.")
            else:
                flash(f"Catalog {catalog.title} has been updated.")
                return redirect(url_for("catalogs.catalog_view", catalog_id=catalog_id))
    form.title.data = catalog.title
    form.description.data = catalog.description
    form.source.data = catalog.source
    return render_template(
        "catalogs/update_form.html",
        form=form,
        title="Update Catalog",
        catalog=catalog,
    )


@bp.route("/<int:catalog_id>/delete", methods=["GET"])
def catalog_delete(catalog_id: int):
    catalog = CatalogFile.query.get_or_404(catalog_id)
    db.session.delete(catalog)
    db.session.commit()
    Path(catalog.filename).unlink()
    flash(f"Catalog {catalog.title} has been deleted.")
    return redirect((url_for("catalogs.catalogs_list")))


@bp.route("/<int:catalog_id>/control/<string:control_id>", methods=["GET"])
def control_view(catalog_id: int, control_id: str):
    catalog_data = CatalogFile.query.get_or_404(catalog_id)
    catalog = CatalogModel.from_json(catalog_data.filename)
    group = catalog.get_group(control_id)
    control = catalog.get_control(control_id)
    guidance = control.guidance
    parameters = control.parameters
    statement = control.statement
    statements = replace_odps(statement, parameters)
    links = get_control_links(control.links, catalog.back_matter)
    return render_template(
        "catalogs/control.html",
        control=control,
        links=links,
        statement=statements,
        catalog=catalog_data,
        guidance=guidance,
        group=group,
    )
