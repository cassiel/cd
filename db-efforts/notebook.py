# /// script
# dependencies = [
#     "flask==3.1.3",
#     "flask-migrate==4.1.0",
#     "flask-sqlalchemy==3.1.1",
#     "marimo",
#     "pandas==3.0.2",
# ]
# requires-python = ">=3.14"
# ///

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium", css_file="./css/marimo.css")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # CD Database

    Database for Plex-hosted music:

    - Ripped physical CDs
    - Bandcamp pure downloads (FLAC) - including albums which were also bought as physical CDs
    - Archival: notes of MP3 rips in Apple Music on the old server

    Source: folder listings as CSV from old and current server, plus notes from Emacs org-mode tables
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Inline Model

    We can inline the model in the notebook, since we now invoke the migration machinery here as well.

    We probably don't care about a Flask server&mdash;we can work purely in the notebook for now&mdash;but we'll build it anyway.
    """)
    return


@app.cell
def model():
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    from flask_migrate import Migrate

    import os
    DB_FILE = os.path.join(os.getcwd(), 'cd.sqlite')

    # Added root_path:
    app = Flask(__name__, root_path=os.getcwd())

    # Danger Will Robinson: I don't know if this is robust for spaces etc. in filenames:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DB_FILE

    db = SQLAlchemy(app)

    # --- MODEL ---

    # Artist 1-m Album:
    class Artist(db.Model):
        __tablename__ = 'artists'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(), unique=True, nullable=False)

        albums = db.relationship('Album', backref='artist')

        def __repr__(self):
            return '<Artist %r>' % self.name

    class Album(db.Model):
        __tablename__ = 'albums'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(), unique=True, index=True, nullable=False)
        is_physical = db.Column(db.Boolean, default=False, nullable=False)
        purchased = db.Column(db.Date, nullable=True)  # We don't know dates for old items,
        encoded = db.Column(db.Date, nullable=True)    # We might enter items before ripping.

        artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)

        def __repr__(self):
            return '<Album %r>' % self.name

    # --- END ---

    migrate = Migrate(app, db)
    return Album, Artist, app, db, os


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Data Ingest

    We use Pandas to pull our CSV data into a data frame. (If you really want to write your own CSV parser to read the file in manually, knock yourself out.)

    The `Modified` field is literally modification date (and also time, to the nearest minute). We'll probably call it something else in the model. For more recent purchases we have manually noted the purchase date as well. A data item we want to incorporate at some stage: year of release.

    Note that we have to nudge Pandas to read the `Modified` column as a date, and not a string.
    """)
    return


@app.cell
def _():
    import pandas as pd

    frame = pd.read_csv("borg.csv", parse_dates=["Modified"])
    frame
    return (frame,)


@app.cell
def _(mo):
    mo.md(r"""
    ## Database Build

    We need to do a one-shot setup of the database, by doing a migration step to get the model loaded up into tables and key constraints.

    We have been doing this by using an external script (called `flask`) from the command line, but we can make Python calls directly in this notebook instead. We need to use the application (model) context (`app.app_context()`) for any database operations.
    """)
    return


@app.cell
def _():
    import flask_migrate

    return (flask_migrate,)


@app.cell
def _(mo):
    mo.md(r"""
    Here's the database initialisation phase. We only attempt it if the `migrations` folder doesn't exist on disk already (in which case the database should not be there either).
    """)
    return


@app.cell
def _(app, flask_migrate, os):
    MIGRATIONS = os.path.join(os.getcwd(), 'migrations')

    if os.path.exists(MIGRATIONS):
        print("Migrations already in place")
    else:
        with app.app_context():
            flask_migrate.init()
    return


@app.cell
def _(mo):
    mo.md(r"""
    Applying migrations is idempotent, so it runs whenever the notebook does (a no-op if the database is already at the head revision). *Generating* a new migration is deliberate: enter a message and press the button. (`migrations/env.py` also discards the revision if the model hasn't changed.)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # `migrations/env.py` change log

    ## Summary
    Fixed a stale-closure bug that disabled the empty-revision guard when `upgrade()` ran before `migrate()` in the same process.

    ## Location
    `migrations/env.py`, `run_migrations_online()`, lines 93-101

    ## Diff
    ```diff
    @@ -90,7 +90,13 @@ def run_migrations_online():
                     directives[:] = []
                     logger.info('No changes in schema detected.')

    -    conf_args = current_app.extensions['migrate'].configure_args
    +    # Work on a copy: env.py is re-executed on every Alembic command, and
    +    # `process_revision_directives` closes over this run's `config`. Storing
    +    # it in the shared dict would leave later runs (e.g. `migrate` after an
    +    # `upgrade` in the same long-lived process) using a stale closure whose
    +    # `cmd_opts` lacks `autogenerate`, silently disabling the empty-revision
    +    # check.
    +    conf_args = dict(current_app.extensions['migrate'].configure_args)
         if conf_args.get("process_revision_directives") is None:
             conf_args["process_revision_directives"] = process_revision_directives
    ```

    ## Changes
    - **Functional:** `conf_args` is now a copy (`dict(...)`) of the shared `configure_args`, not the shared dict itself.
    - **Documentation:** a 6-line comment explains the reason.
    - **Unchanged:** the guard function, the `is None` check, and support for a user-supplied `process_revision_directives`.

    ## Root cause
    1. Alembic re-executes `env.py` on every command.
    2. The guard was stored in the shared dict on the first run and reused afterwards.
    3. It closed over the first run's `config`. If that run was `upgrade()`, `cmd_opts` had no `autogenerate` flag, so the guard never fired.

    ## Before and after
    - **Before:** `migrate()` with no model change, after an earlier `upgrade()`, wrote an empty revision.
    - **After:** it logs "No changes in schema detected." and writes no file.

    ## Verification
    - **Before the fix:** the second button press with no model change created `e04f71bcd631_should_not_be_created.py`.
    - **After the fix:** the same sequence created no file, and the DB stayed at `af1264b0884d`.
    - **Scope:** both runs used scratch copies. The real DB remained at `870a1e097c0d`.
    """)
    return


@app.cell
def _(app, flask_migrate):
    with app.app_context():
        flask_migrate.upgrade()
    upgraded = True
    return (upgraded,)


@app.cell
def _(mo):
    migration_message = mo.ui.text(label="Migration message", full_width=True)
    generate_button = mo.ui.run_button(label="Generate migration")
    mo.hstack([migration_message, generate_button], justify="start")
    return generate_button, migration_message


@app.cell
def _(app, flask_migrate, generate_button, migration_message, mo, upgraded):
    # Only runs when the button is pressed (not on reactive re-execution),
    # and only after the database has been brought up to date, since
    # autogenerate refuses to run against an out-of-date database.
    mo.stop(not generate_button.value or not upgraded)
    mo.stop(
        not migration_message.value.strip(),
        mo.md("**Enter a migration message first.**"),
    )

    with app.app_context():
        flask_migrate.migrate(message=migration_message.value.strip())
        flask_migrate.upgrade()
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Database Load

    We drop all database content (but *not* table structure) and then load up. We (probably(*)) need to remove the albums first before the things that albums refer to. When populating, we need to put in the referred-to items first, because we have to look them up (by name) when we link in the albums.

    (*TODO*: establish a sensible cascade policy.)
    """)
    return


@app.cell
def _(Album, Artist, app, db, frame):
    # Delete any locations and objects first:

    with app.app_context():
        Album.query.delete()
        Artist.query.delete()
        db.session.commit()

    # Add all unique artists (there should not be any nulls!).
    with app.app_context():
        for _name in frame["Artist"].drop_duplicates():
            _artist = Artist(name=_name)
            print(_artist)
            db.session.add(_artist)
        db.session.commit()

    # Finally: iterate over all albums, picking up
    # all the other properties along the way:
    with app.app_context():
        for _row in frame.itertuples():
            print(_row)
            _artist_name = _row.Artist
            _artist = Artist.query.filter_by(name=_artist_name).first()

            _a = Album(name=_row.Album, artist=_artist, label=_label, format=_format)
            db.session.add(_a)
        db.session.commit()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Example Queries

    - For each query we build a statement using the likes of `select` and additional methods like `where()`
    - While the session is active, we can extract properties of the objects returned (but not afterwards)
    """)
    return


@app.cell
def _(Artist, app, db):
    from sqlalchemy import select

    # A simple selection without filtering. We get a single artist
    # (an array of one value) and multiple albums for that artist.

    _stmt = select(Artist).where(Artist.name == "Various Artists")

    print(_stmt)

    with app.app_context():
        _result = db.session.execute(_stmt)
        _values = [x.albums for x in _result.scalars()]

    _values
    return (select,)


@app.cell
def _(Artist, app, db, select):
    # A slightly better filtering when we know our select() only
    # returns one value. (It still comes back as a "tuple" of one value.)

    _stmt = select(Artist).where(Artist.name == "Various Artists")

    print(_stmt)

    with app.app_context():
        _result = db.session.execute(_stmt).first()
        _values = _result[0].albums

    #type(_result)
    _values
    return


@app.cell
def _(Album, Artist, app, db, select):
    # Here we are querying two tables to find an artist given
    # the name of one of the albums. The result row has two
    # items (artist id and name).

    from sqlalchemy import and_, or_

    _stmt = select(Artist.id, Artist.name).where(
        and_(
            Album.name == "Cyclone",
            Album.artist_id == Artist.id
        )
    )

    print(_stmt)

    with app.app_context():
        _result = db.session.execute(_stmt).first()

    _result
    return


if __name__ == "__main__":
    app.run()
