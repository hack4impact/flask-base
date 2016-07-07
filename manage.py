#!/usr/bin/env python
import os
from app import create_app, db
from app.models import User, Role
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

# The following code block will look for a '.env' file which
# contains environment variables for things like email address
# and any other env vars. The .env file will be parsed and
# santized. Each line contains some "NAME=VALUE" pair. Split
# this and then store var[0] = "NAME" and var[1] = "VALUE".
# Then formally set the environment variable in the last line of
# this block. Per our running example, os.environ["NAME"] = "VALUE"
# These environment variables can be accessed with "os.getenv('KEY')"

if os.path.exists('.env'):
    print('Importing environment from .env file')
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]

# Refer to manage.py for more details. Currently the application will
# look for an environment variable called 'FLASK_CONFIG' or it will
# move to the 'default' configuration which is the DevelopmentConfig
# (again see manage.py for full details). Next it will call the
# create_app method found in app/__init__.py. This method takes in a
# name of a configuration and finds the configuration settings in
# config.py. In heroku this will be set to 'production' i.e.
# ProductionConfig. Next a 'Manager' instance is created. Manager
# is basically a nice plugin(?) that will allow us to get some useful
# feedback when we call manage.py from the command line. It also handles
# all the manage.py commands. The @manager.command and @manager.option(...)
# decorators are used to determine what the help output should be
# on the terminal. Migrate is used to make migration between db instances
# really easy.

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

# Make shell context doesn't really serve a ton of purpose in most of our
# development at h4i. However, it is entirely possible to explore the database
# from the command line with this as seen in the lines below.


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)

# It is possible to create a general app shell or database specific shell.
# For example doing 'python manage.py shell'
# $ me = User()
# $ db.session.add(me) && db.session.commit()
# $ me.id
# >> 1
# This basically creates a new user object, commits it to the database gives
# it a id. The db specific shell exposes the native MigrateCommands...
# honestly you won't have to worry about these and future info can
# be found the Flask-Migrate documentation

manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

# ... you should make unit tests. python manage.py test


@manager.command
def test():
    """Run the unit tests."""
    import unittest

    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

# So this will clear out all the user data (drop_all), will create a new
# database but with all the tables and columns set up per your models.
# create_all() and drop_all() rely upon the fact that you have imported
# ** ALL YOUR DATABASE MODELS **. If you are seeing some table not being
# created this is the most likely culprit.


@manager.command
def recreate_db():
    """
    Recreates a local database. You probably should not use this on
    production. EDIT: SHOULD NOT USE THIS IN PRODUCTION!!!
    """
    db.drop_all()
    db.create_all()
    db.session.commit()

# Self expanatory. See app/models/user.py for details


@manager.option('-n',
                '--number-users',
                default=10,
                type=int,
                help='Number of each model type to create',
                dest='number_users')
def add_fake_data(number_users):
    """
    Adds fake data to the database.
    """
    User.generate_fake(count=number_users)

# The setup_dev and setup_prod commands currently point to the
# setup_general() method which initializes two role objects in
# the database. A 'User' and an 'Administrator'. These roles
# are needed in order to create a valid user in this system
# since all users are tied to a role type.


@manager.command
def setup_dev():
    """Runs the set-up needed for local development."""
    setup_general()


@manager.command
def setup_prod():
    """Runs the set-up needed for production."""
    setup_general()


def setup_general():
    """Runs the set-up needed for both local development and production."""
    Role.insert_roles()

# You may/may not know this but the whole
# if __name__ == '__main__' check is to see if this file is being executed
# directly rather than indirectly (by being imported through another file).
# So when we execute this file directly (by running python manage.py SOMECMD)
# we get the option of instatiating the manager instance
# These methods should be accessible from other
# files though if imported. << HAVE NOT TESTED THIS THEORY OUT
# But you would have a tough time executing these commands from cmd line
# without the Manager init (otherwise you have to deal with argvs and
# stuff that is frankly tedious).

if __name__ == '__main__':
    manager.run()
