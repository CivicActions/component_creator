import logging
from pathlib import Path

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


def component_create_file(data: dict) -> str:
    filename = secure_filename(data.get("name"))
    base_path = Path(current_app.config["UPLOAD_FOLDER"]).joinpath("components")
    if not base_path.is_dir():
        base_path.mkdir(mode=0o755, parents=True, exist_ok=False)

    components = Component(
        title=data.get("name"),
        description=data.get("description"),
    )
    metadata = Metadata(
        title=data.get("name"),
        version="0.0.1",
    )
    component_definition = ComponentDefinition(
        metadata=metadata, components=[components]
    )
    component = ComponentModel(component_definition=component_definition)
    filepath = base_path.joinpath(filename).with_suffix(".json")
    write_component_file(filepath, component)

    return filepath.as_posix()


def load_component_file(filepath: str) -> ComponentModel:
    try:
        component = ComponentModel.from_json(filepath)
        return component
    except EnvironmentError as exc:
        flash(f"There was an error loading the component file: {filepath}.", "error")
        current_app.logger(f"Error loading component: {exc}")


def write_component_file(filepath: Path, definition: ComponentModel):
    json_file = definition.json(indent=2)
    try:
        with open(filepath, "w+") as f:
            f.write(json_file)
    except IOError as exc:
        flash("Error writing Component file.", "error")
        logging.error(f"Error writing file {filepath}: {exc}")


def add_implemented_requirement(control_id: str) -> ImplementedRequirement:
    return ImplementedRequirement(
        control_id=control_id,
        description="Add Control narrative",
    )


def add_implementations(
    component_data: ComponentFile, catalog_id: int, control_id: str
):
    definition = load_component_file(component_data.filename)
    catalog = CatalogFile.query.get_or_404(catalog_id)

    component = definition.component_definition.components[0]
    if check_existing_implementaton(catalog.source, component.control_implementations):
        component = update_control_implementation(component, control_id)
    else:
        component = add_control_implementation(component, catalog, control_id)
    definition.component_definition.components[0] = component
    write_component_file(Path(component_data.filename), definition)


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


def update_control_implementation(component: Component, control_id: str) -> Component:
    requirement = add_implemented_requirement(control_id)
    component.control_implementations.implemented_requirements.append(requirement)
    return Component


def check_existing_implementaton(source: str, implementation: list) -> bool:
    for ci in implementation:
        if ci["source"] == source:
            return True
    return False


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
            if "component_file" in request.files:
                file = request.files["component_file"]
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                base_path = Path(current_app.config["UPLOAD_FOLDER"]).joinpath(
                    "components"
                )
                if not base_path.is_dir():
                    base_path.mkdir(parents=True, exist_ok=False)
                filepath = base_path.joinpath(filename).as_posix()
                request.files["component_file"].save(filepath)
            else:
                filepath = component_create_file(
                    {
                        "name": title,
                        "description": description,
                        "type": component_type,
                    }
                )

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

    component = load_component_file(component_data.filename)
    file = Path(component_data.filename)

    return render_template(
        "components/component.html",
        component=component_data,
        json=component,
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
