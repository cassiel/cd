# /// script
# dependencies = [
#     "marimo",
# ]
# requires-python = ">=3.14"
# ///

import marimo

__generated_with = "0.23.3"
app = marimo.App(width="medium", css_file="../css/marimo.css")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Migration

    We now need to start to leave notebooks behind, since the various Flask-based migration tools expect to find source files with configuration statements.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We're going to start doing command-line tasks now, as we get our database migrations to work. So we use the Conda-installed `pip` to set up the tools for the command line, not just for individual notebooks:

    `$ pip install flask-migrate`

    (Double-check you're installing into the right Conda environment.)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    See what we've done in `app.py`. Before we can do any migrations, we have to initialise the folder of migration steps. (This is a shell command, not Python. On Windows, try using `%%cmd`.)

    `$ flask db init`
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    If we try to build a migration step right now:

    `$ flask db migrate`

    it will run, but since the main script knows nothing about the model (`User`, `Role`) it will remove these tables from the database! So:

    - Remove this migration step
    - Add the model classes to the main script (`app.py`) - I've created a second script called `app_with_model.py` which I refer to below
    - Run the migration again with this model:

    `$ flask -A app_with_model db migrate -m "First migration."`

    - Notice that nothing has to be done: the database is already consistent with the model

    Quick exercise: remove the database completely, and *then* create a migration step. Notice that the code regenerates the tables and key linkage.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now run the upgrade to actually alter the database.

    `flask -A app_with_model db upgrade`
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Browse the database, notice that everything is there, as well as an additional table which tracks the migration steps.

    Finally: make a change to the model (for example, add a new field to `User`). Create, check and run the migration.

    If we add a unique email address field, the migration code is slightly faulty (the constraint needs a name), so this one does need a manual edit.
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
