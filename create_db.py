import argparse

parser = argparse.ArgumentParser(description='Create a new database for Flask app')
parser.add_argument(
    "destination",
    choices=["render", "local"],  # Restrict choices to "render" or "local"
    help="Specify the destination: PostgreSQL on Render or Local"
)
args = parser.parse_args()

######### Create db for Local #########
if args.destination == "local":
    from project.app import app, db

    with app.app_context():
        # create the database and the db table
        db.create_all()

        # commit the changes
        db.session.commit()

elif args.destination == "render":
    ######### Create db for PostgreSQL on Render #########
    from pathlib import Path
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy

    ### Copied from app.py
    basedir = Path(__file__).resolve().parent

    DATABASE = "flaskr.db"
    USERNAME = "admin"
    PASSWORD = "admin"
    SECRET_KEY = "change_me"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    url = "postgresql://flask_blog_db_8zmd_user:4nkmQb8uslrnsQNYCZs339HMfqKt5PJl@dpg-crurm208fa8c73f0v1sg-a.oregon-postgres.render.com/flask_blog_db_8zmd"
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = url

    app = Flask(__name__)
    app.config.from_object(__name__)
    db = SQLAlchemy(app)


    ###

    ### Copied from models.py
    class Post(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String, nullable=False)
        text = db.Column(db.String, nullable=False)

        def __init__(self, title, text):
            self.title = title
            self.text = text

        def __repr__(self):
            return f'<title {self.title}>'


    ###

    ### Create the database and the db table
    with app.app_context():
        db.create_all()
        db.session.commit()
    exit(0)
