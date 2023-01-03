from pathlib import Path
from typing import Optional

from flask import (
    Markup,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from jinja2 import TemplateNotFound
from werkzeug.utils import secure_filename

from app.components import bp
from app.components.forms import ComponentForm
from app.extensions import db
from app.models.components import CatalogFile, ComponentFile
from app.oscal.catalog import CatalogModel
from app.oscal.component import (
    Component,
    ComponentDefinition,
    ComponentModel,
    ControlImplementation,
    ImplementedRequirement,
    Metadata,
)

ALLOWED_EXTENSIONS = {"json"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def component_create_file(component_file: ComponentFile):
    components = Component(
        title=component_file.title,
        description=component_file.description,
    )
    metadata = Metadata(
        title=component_file.title,
        version="0.0.1",
    )
    component_definition = ComponentDefinition(
        metadata=metadata, components=[components]
    )
    component = ComponentModel(component_definition=component_definition)
    component_file.write_file(component)


def add_implemented_requirement(control_id: str) -> ImplementedRequirement:
    return ImplementedRequirement(
        control_id=control_id,
        description="Add Control narrative",
    )


def add_implementations(
    component_data: ComponentFile, catalog_id: int, control_id: str
):
    definition = ComponentModel.from_json(component_data.filename)
    catalog = CatalogFile.query.get_or_404(catalog_id)

    component = definition.component_definition.components[0]
    implemented_index = check_existing_implementation(
        catalog.source, component.control_implementations
    )
    if implemented_index and implemented_index >= 0:
        ir = add_implemented_requirement(control_id)
        component.control_implementations[
            implemented_index
        ].implemented_requirements.append(ir)
    else:
        component = add_control_implementation(component, catalog, control_id)
    definition.component_definition.components[0] = component
    component_data.write_file(definition)


def add_control_implementation(
    component: Component, catalog: CatalogFile, control_id: str
) -> Component:
    requirement = add_implemented_requirement(control_id)
    component.control_implementations.append(
        ControlImplementation(
            source=catalog.source,
            description=catalog.title,
            implemented_requirements=[requirement],
        )
    )
    return component


def check_existing_implementation(source: str, implementation: list) -> Optional[int]:
    for key, ci in enumerate(implementation):
        if ci.source == source:
            return key
    return None


def check_existing_control(control_id: str, requirement: list) -> bool:
    for ir in requirement:
        if ir["control-id"] == control_id:
            return True
    return False


@bp.route("/", methods=["GET"])
def components_list():
    components = ComponentFile.query.all()

    if not components:
        flash(
            message="There are no Components installed. Click the link below to create or upload one.",
            category="message",
        )

    try:
        return render_template("components/list.html", components=components)
    except TemplateNotFound:
        abort(404)


@bp.route("/create", methods=["GET", "POST"])
def component_create():
    form = ComponentForm()
    if request.method == "POST":
        error = None
        file = None
        if form.validate_on_submit():
            title = form.title.data
            description = form.description.data
            component_type = form.component_type.data

            base_path = Path(current_app.config["UPLOAD_FOLDER"]).joinpath("components")
            if not base_path.is_dir():
                base_path.mkdir(parents=True, exist_ok=False)

            if "component_file" in request.files:
                file = request.files["component_file"]
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = base_path.joinpath(filename).as_posix()
                request.files["component_file"].save(filepath)
            else:
                filename = secure_filename(title)
                filepath = base_path.joinpath(filename).with_suffix(".json").as_posix()

            try:
                component = ComponentFile(
                    title=title,
                    description=description,
                    type=component_type,
                    filename=filepath,
                )
                db.session.add(component)
                db.session.commit()
            except db.SQLAlchemyError as exc:
                error = f"Component {title} already exists: {exc}"
            else:
                if not file:
                    component_create_file(component)
                flash(f"Component {title} created.", "message")
                return redirect(
                    url_for("components.component_view", component_id=component.id)
                )
        flash(error)
    return render_template(
        "components/create_form.html", form=form, title="Add Component"
    )


@bp.route("/<int:component_id>", methods=["GET"])
def component_view(component_id: int):
    component_data = ComponentFile.query.get_or_404(component_id)
    catalogs = CatalogFile.query.all()

    if not catalogs:
        flash(
            message=Markup(
                "At least one Catalog is required in order to add Controls to your Component "
                "<a href='/catalogs/create'>Add a Catalog</a>"
            ),
            category="warning",
        )

    json = ComponentModel.from_json(component_data.filename)

    file = Path(component_data.filename)

    return render_template(
        "components/component.html",
        component=component_data,
        json=json,
        filename=file.name,
        catalogs=catalogs,
    )


@bp.route("/download/<path:filename>", methods=["GET"])
def component_file_download(filename: str):
    upload_dir = Path(current_app.config["UPLOAD_FOLDER"]).joinpath("components")
    return send_from_directory(directory=upload_dir, path=filename)


@bp.route("<int:component_id>/add/catalog/<int:catalog_id>", methods=["GET"])
def component_add_catalog(component_id: int, catalog_id: int):
    component = ComponentFile.query.get_or_404(component_id)
    catalog = CatalogFile.query.get_or_404(catalog_id)
    if catalog.id not in component.catalogs:
        try:
            component.catalogs.append(catalog)
            db.session.add(component)
            db.session.commit()
        except db.SQLAlchemyError as exc:
            flash(f"Unable to add Catalog: {catalog.title}: {exc}")
        else:
            flash(f"Catalog {catalog.title} added.", "message")
    else:
        flash(f"Catalog {catalog.title} already added to {component.title}", "error")

    return redirect(url_for("components.component_view", component_id=component.id))


@bp.route("<int:component_id>/catalog/<int:catalog_id>", methods=["GET"])
def component_show_catalog(component_id: int, catalog_id: int):
    component = ComponentFile.query.get_or_404(component_id)
    catalog_data = CatalogFile.query.get_or_404(catalog_id)
    catalog = CatalogModel.from_json(catalog_data.filename)
    metadata = catalog.metadata
    groups = catalog.get_groups()
    return render_template(
        "components/control_add_form.html",
        component=component,
        metadata=metadata,
        groups=groups,
        catalog=catalog_data,
    )


@bp.route(
    "<int:component_id>/catalog/<int:catalog_id>/<string:control_id>", methods=["GET"]
)
def component_add_control(component_id: int, catalog_id: int, control_id: str):
    component_data = ComponentFile.query.get_or_404(component_id)
    add_implementations(component_data, catalog_id, control_id)

    return redirect(url_for("components.component_view", component_id=component_id))
