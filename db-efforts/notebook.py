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

__generated_with = "0.24.0"
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

    # Format 1-m Album (should probably be m-m for Bandcamp CD plus download, but for now...)
    class Format(db.Model):
        __tablename__ = 'formats'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(), unique=True, nullable=False)

        albums = db.relationship('Album', backref='format')

        def __repr__(self):
            return '<Format %r>' % self.name

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

        artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
        format_id = db.Column(db.Integer, db.ForeignKey('formats.id'))

        def __repr__(self):
            return '<Album %r>' % self.name

    # --- END ---

    migrate = Migrate(app, db)
    return Album, Artist, Format, app, db, os


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Data Ingest

    We use Pandas to pull our CSV data into a data frame. (If you really want to write your own CSV parser to read the file in manually, knock yourself out.) Unlike in Session 7, we don't use Pandas to connect to the database at all&mdash;that's all done with the model and SQLAlchemy.

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
def _(app, flask_migrate):
    with app.app_context():
        flask_migrate.migrate(message="Initial migration to establish model.")
    return


@app.cell
def _(app, flask_migrate):
    with app.app_context():
        flask_migrate.upgrade()
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Database Load

    We drop all database content (but *not* table structure) and then load up. We (probably(*)) need to remove the albums first before the things that albums refer to. When populating, we need to put in the referred-to items first, because we have to look them up (by name) when we link in the albums.

    > (*) What happens if we attempt to remove the dependencies of albums before we remove the albums themselves depends on how the database has been set up: I refer the interested reader to tutorials on SQLAlchemy's [cascade](https://docs.sqlalchemy.org/en/21/orm/cascades.html) machinery.
    """)
    return


@app.cell
def _(Album, Artist, Format, Label, app, db, frame):
    # Delete any locations and objects first:

    with app.app_context():
        Album.query.delete()
        Artist.query.delete()
        Label.query.delete()
        Format.query.delete()
        db.session.commit()

    # Purge any records where the format name is missing:
    _f = frame.dropna(subset=["Format"])

    # Add all unique formats.
    with app.app_context():
        for _name in _f["Format"].drop_duplicates():
            _format = Format(name=_name)
            print(_format)
            db.session.add(_format)
        db.session.commit()

    # Add all unique artists (there should not be any nulls!).
    # NOTE: we iterate over `frame` (not `_f`) otherwise
    # we'll miss any artist whose albums have no recorded format.
    with app.app_context():
        for _name in frame["Artist"].drop_duplicates():
            _artist = Artist(name=_name)
            print(_artist)
            db.session.add(_artist)
        db.session.commit()

    # Add labels (might be null, as for formats):
    _f = frame.dropna(subset=["Label"])

    with app.app_context():
        for _name in _f["Label"].drop_duplicates():
            _label = Label(name=_name)
            print(_label)
            db.session.add(_label)
        db.session.commit()

    # Finally: iterate over all albums, picking up
    # all the other properties along the way:

    with app.app_context():
        for _row in frame.itertuples():
            print(_row)
            _format_name = _row.Format
            _format = Format.query.filter_by(name=_format_name).first()

            _label_name = _row.Label
            _label = Label.query.filter_by(name=_label_name).first()

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
