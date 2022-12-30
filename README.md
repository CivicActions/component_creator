# Component Creator

A Python Flask app for creating [OSCAL](https://pages.nist.gov/OSCAL/) compliance components.

## Flask

[Flask](https://flask.palletsprojects.com/en/2.2.x/) is a lightweight Python web application framework using the
[Jinja](https://jinja.palletsprojects.com/en/3.1.x/) templating language and the
[Werkzeug](https://palletsprojects.com/p/werkzeug/) WSGI toolkit and [SQLite](https://www.sqlite.org/index.html).

### Poetry

The application's dependencies and virtual environments are managed using [Python Poetry](https://python-poetry.org/).


### Set up

- Clone the repe
- Change directory into the repo: `cd component_editor`
- Run `poetry install` to install the project dependencies.
- Instantiate the database by running `poetry run flask --app app init-db`
- Run the application by running `poetry run flask --app app run`

## Catalogs

This application is designed to [OSCAL formatted Catalog](https://pages.nist.gov/OSCAL/concepts/layer/control/catalog/)
specific [Components](https://pages.nist.gov/OSCAL/concepts/layer/implementation/component-definition/).
You will need to import at least one Catalog. NIST has several resolved catalogs in their
[Github repository](https://github.com/usnistgov/oscal-content/tree/main/nist.gov/SP800-53) which you can use.
Choose a JSON file from either the **rev5** or **rev4** directory, but make sure to choose a Catalog, not a Profile.
For example ***NIST_SP-800-53_rev5_HIGH-baseline-resolved-profile_catalog.json***. These Catalogs are availble to you
but the system should be able to handle any OSCAL formatted Catalog.

### Importing Catalogs

Once you have a Catalog you can import it into the system by clicking **Catalogs** -> **Add a Catalog** from the main
menu and uploading the file. Once you have uploaded the file you will be redirected to the Catalog details page that
show information about the catalog including a list of Controls.

All Catalogs imported into the system will be listed on the `/catalogs` page available from the main menu.
