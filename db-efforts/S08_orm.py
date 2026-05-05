# /// script
# dependencies = [
#     "flask==3.1.3",
#     "flask-sqlalchemy==3.1.1",
#     "jedi<0.20.0",
#     "marimo",
# ]
# requires-python = ">=3.14"
# ///

import marimo

__generated_with = "0.23.4"
app = marimo.App(width="medium", css_file="../css/marimo.css")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Using SQLAlchemy
    ## Nick Rothwell, 2026

    ### Approach 1

    Use Pandas to build a flat database table from the V&A API, and then manually normalise it to add more structure.

    ### Approach 2

    Use Pandas to fetch data from the API (as above), but: build out our own database from a migratable model in Python.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### DB Connection

    When we link up with the Flask server we'll need to build a URL for the database (`sqlite://...`) so we'll take the opportunity right now to make the path absolute:
    """)
    return


@app.cell
def _():
    import os
    DB_FILE = os.path.join(os.getcwd(), 'data.db')

    print(DB_FILE)
    return DB_FILE, os


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Build the Flask application and the SQLAlchemy instance (we can get work done with these even though we aren't using the Flask server right now).
    """)
    return


@app.cell
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
    Here is our <em>Version 1</em> model. We have a `User` class of users with usernames, and a `Role` class of user roles. There's a little bit of database integration here: note that both classes have an `id` field (as a primary key) and a string field (`name` or `username`) for actual data.

    (Both also have a `__repr__` function to print them out neatly.)
    """)
    return


@app.cell(disabled=True)
def _(db):
    # VERSION 1

    class Role(db.Model):
        __tablename__ = 'roles'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(), unique=True)

        def __repr__(self):
            return '<Role %r>' % self.name

    class User(db.Model):
        __tablename__ = 'users'
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(), unique=True, index=True)

        def __repr__(self):
            return '<User %r>' % self.username

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Let's completely wipe out the database before we start:
    """)
    return


@app.cell
def _(DB_FILE, os):
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Here's the boilerplate code to create the database schema from the model (which has been loaded into `db`):
    """)
    return


@app.cell
def _(app, db):
    with app.app_context():
        db.drop_all()
        db.create_all()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    At this stage, take a look at the database in the DB browser. The tables are present, and there's an index on `users.username` (for efficiency, as and when we have lots of users) - but there's nothing linking together the users and the roles. Here's a <em>Version 2</em> update to the model.

    (We've had to use new names - `User2` and `Role2` - because Marimo does not like having multiple cells (re)declaring the same names. This is one of the issues nudging us to write Python "properly" in modular files, not notebooks!)

    There are two steps:

    1. Each user has a link to a role. We add a `role_id` which is a foreign-key link to the table of roles

    1. Each role has a list of users. We add this as a relationship to the `User` class, and include a `backref` which inserts a `role` field into the `User` class

    Run this model again (but <font color="red">NOTE </font> you will need to <em>disable</em> the Version 1 model and restart the kernel, re-establish the `db` context first, and run `db.create_all` once you've read in the model).
    """)
    return


@app.cell
def _(db):
    # VERSION 2

    class Role2(db.Model):
        __tablename__ = 'roles'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(64), unique=True)

        # A role contains users, linked to the User class (and add
        # a role field to User also):
        users = db.relationship('User2', backref='role')

        def __repr__(self):
            return '<Role %r>' % self.name

    class User2(db.Model):
        __tablename__ = 'users'
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(64), unique=True, index=True)

        # The User class has a foreign key link to the roles table:
        role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

        def __repr__(self):
            return '<User %r>' % self.username


    return Role2, User2


@app.cell
def _(Role2, User2):
    admin_role = Role2(name='Admin')
    mod_role = Role2(name='Moderator')
    user_role = Role2(name='User')
    user_john = User2(username='john', role=admin_role)
    user_susan = User2(username='susan', role=user_role)
    user_david = User2(username='david', role=user_role)
    return admin_role, mod_role, user_david, user_john, user_role, user_susan


@app.cell
def _(
    admin_role,
    app,
    db,
    mod_role,
    user_david,
    user_john,
    user_role,
    user_susan,
):
    with app.app_context():
        db.session.add_all([admin_role, mod_role, user_role,
                            user_john, user_susan, user_david])
        db.session.commit()
    return


@app.cell
def _(Role2, User2, app):
    with app.app_context():
        print("* All users")
        print(User2.query.all())
        print("* Users with role 'User'")
        role = Role2.query.filter_by(name="User").first()
        print("(Users, filtered by role)")
        print(User2.query.filter_by(role=role).all())
        print("(All the users attached to this role)")
        print(role.users)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    See also: use of `lazy="dynamic"` to defer queries so that they can be filtered (`role.users.filter_by(...).all()`).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Simple Exercise

    Add a new user with the role of `Moderator`. Query all users to see that this has been done, and check the database directly too.
    """)
    return


if __name__ == "__main__":
    app.run()
