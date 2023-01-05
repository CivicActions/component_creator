import os

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))

load_dotenv()


class Config:
    INSTANCE_PATH = os.path.join(basedir, "instance")
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI") or "sqlite:///" + os.path.join(
        INSTANCE_PATH, "app.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    BASEPATH = basedir
    UPLOAD_FOLDER = os.path.join(basedir, "app/files")
    FLASK_ENV = "development"
    WTF_CSRF_ENABLED = True
    CSRF_SESSION_KEY = os.getenv("CSRF_SESSION_KEY")


class TestConfig:
    INSTANCE_PATH = os.path.join(basedir, "instance")
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI") or "sqlite:///" + os.path.join(
        INSTANCE_PATH, "testing.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(basedir, "tests/data")
    # Enable the TESTING flag to disable the error catching during request handling
    # so that you get better error reports when performing test requests against the application.
    TESTING = True
    # Disable CSRF tokens in the Forms (only valid for testing purposes!)
    # WTF_CSRF_ENABLED = False
    CSRF_SESSION_KEY = os.getenv("CSRF_SESSION_KEY")
