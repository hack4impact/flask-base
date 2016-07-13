#!/usr/bin/env python
import os
from app import create_app, db
from app.models import User, Role
from redis import Redis
from rq import Worker, Queue, Connection
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

# A note about python manage.py runserver. Runserver is
# actually located in flask.ext.script. Since we
# have not specified a runserver command, it defaults to
# flask.ext.script's Server() method which calls the native
# flask method app.run(). You can pass in some arguemnts such
# as changing the port on which the server is run.
#
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
# really easy. Additionally @manager.command creates an application
# context for use of plugins that are usually tied to the app.

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

# Make shell context doesn't really serve a ton of purpose in most of our
# development at h4i. However, it is entirely possible to explore the database
# from the command line with this as seen in the lines below.


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    """Run the unit tests."""
    import unittest

    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@manager.command
def recreate_db():
    """
    Recreates a local database. You probably should not use this on
    production.
    """
    db.drop_all()
    db.create_all()
    db.session.commit()


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


@manager.command
def run_worker():
    """Initializes a slim rq task queue."""
    listen = ['default']
    conn = Redis(
        host=app.config['RQ_DEFAULT_HOST'],
        port=app.config['RQ_DEFAULT_PORT'],
        db=0,
        password=app.config['RQ_DEFAULT_PASSWORD']
    )

    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()

if __name__ == '__main__':
    manager.run()
