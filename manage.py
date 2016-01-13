#!/usr/bin/env python
import os
import time
from app import create_app, db
from app.models import User, Role
from redis import Redis
from rq import Worker, Queue, Connection
from rq_scheduler.scheduler import Scheduler
from rq_scheduler.utils import setup_loghandlers
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand


# Import settings from .env file. Must define FLASK_CONFIG
if os.path.exists('.env'):
    print('Importing environment from .env file')
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


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


@manager.command
def run_scheduler():
    """Initializes a rq scheduler."""
    conn = Redis(
        host=app.config['RQ_DEFAULT_HOST'],
        port=app.config['RQ_DEFAULT_PORT'],
        db=0,
        password=app.config['RQ_DEFAULT_PASSWORD']
    )

    setup_loghandlers('INFO')
    scheduler = Scheduler(connection=conn, interval=60.0)
    for _ in xrange(10):
        try:
            scheduler.run()
        except ValueError, exc:
            if exc.message == 'There\'s already an active RQ scheduler':
                scheduler.log.info(
                    'An RQ scheduler instance is already running. Retrying in '
                    '%d seconds.', 10,
                )
                time.sleep(10)
            else:
                raise

if __name__ == '__main__':
    manager.run()
