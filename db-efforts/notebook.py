# /// script
# dependencies = [
#     "flask==3.1.3",
#     "flask-migrate==4.1.0",
#     "flask-sqlalchemy==3.1.1",
#     "marimo",
# ]
# requires-python = ">=3.14"
# ///

import marimo

__generated_with = "0.20.4"
app = marimo.App(width="medium", css_file="css/marimo.css")


@app.cell
def _():
    return


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # CD Database Development
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Setup

    (See also the `app.py` model file for DB filename, when we start migrations.)

    <em>TEST ME</em> : could we import `app.py` here and use `DB_FILE` and friends?
    """)
    return


@app.cell
def _():
    import os
    DB_FILE = os.path.join(os.getcwd(), 'cd.sqlite')

    print(DB_FILE)
    return DB_FILE, os


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Build the Flask application and the SQLAlchemy instance (we can get work done with these even though we aren't using the Flask server right now). Implicitly here there's an empty model.
    """)
    return


@app.cell(disabled=True)
def _(DB_FILE):
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy

    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DB_FILE

    db = SQLAlchemy(app)
    return app, db


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Console Tools

    `$ pip install flask-migrate`

    (Maybe a `which pip` first to double-check it's the Conda one and targetting the correct environment.)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Model

    Working with everything in `app.py` for now. We kick off with an empty model and set up the migration machinery and state.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Admin

    How to wipe the database completely:
    """)
    return


@app.cell(disabled=True)
def _(DB_FILE, os):
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Initial database build:
    """)
    return


@app.cell(disabled=True)
def _(app, db):
    with app.app_context():
        db.drop_all()
        db.create_all()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Refactoring

    Can we work with `app.py`? Yes, apparently. (This will pull `flask-migrate` and friends into our notebook environment, although for the terminal calls we use the ones in Conda. <em>NOTE</em> : make sure these stay consistent&mdash;or else, deprecate the use of `uv` and have a dedicated Conda environment for this notebook, having checked that dependencies can be auto-resolved as with `uv`.)
    """)
    return


@app.cell
def _():
    import app as A

    return (A,)


@app.cell
def _(A):
    with A.app.app_context():
        A.db.drop_all()
        A.db.create_all()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Before we can do any migrations, we have to initialise the folder of migration steps. The source `app.py` is read by default (or else, specify with `flask -A filename ...`).

    `$ flask db init`

    Generate migration steps with:

    `$ flask db migrate`

    Commit migrations with:

    `$ flask -A app_with_model db migrate -m "<migration name>"`
    """)
    return


if __name__ == "__main__":
    app.run()
