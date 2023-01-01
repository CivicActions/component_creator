from pathlib import Path

from flask import (
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
from app.models.components import ComponentFile
from app.oscal.component import Component, ComponentDefinition, ComponentModel, Metadata

ALLOWED_EXTENSIONS = {"json"}


def allowed_file(filename):
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
    json_file = component.json(indent=2)
    with open(filepath, "w+") as f:
        f.write(json_file)

    return filepath.as_posix()


def load_component_file(filepath: str) -> Component:
    try:
        component = ComponentModel.from_json(filepath)
        return component
    except EnvironmentError as exc:
        flash(f"There was an error loading the component file: {filepath}.", "error")
        current_app.logger(f"Error loading component: {exc}")


def control_add(component_id: int, control_id: str) -> dict:
    component = ComponentFile.query.get_or_404(component_id)
    return component


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
def component_view(component_id):
    component_data = ComponentFile.query.get_or_404(component_id)
    component = load_component_file(component_data.filename)
    file = Path(component_data.filename)

    return render_template(
        "components/component.html",
        component=component_data,
        json=component,
        filename=file.name,
    )


@bp.route("/download/<path:filename>", methods=["GET"])
def file_download(filename: str):
    upload_dir = Path(current_app.config["UPLOAD_FOLDER"]).joinpath("components")
    return send_from_directory(directory=upload_dir, path=filename)
