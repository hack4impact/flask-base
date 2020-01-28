# Manage.py and Commands
 
## `python manage.py runserver`

A note about python manage.py runserver. Runserver is
actually located in flask.ext.script. Since we
have not specified a runserver command, it defaults to
flask.ext.script's Server() method which calls the native
flask method app.run(). You can pass in some arguments such
as changing the port on which the server is run.

## `.env`

The following code block will look for a '.env' file which
contains environment variables for things like email address
and any other env vars. The .env file will be parsed and
santized. Each line contains some "NAME=VALUE" pair. Split
this and then store var[0] = "NAME" and var[1] = "VALUE".
Then formally set the environment variable in the last line of
this block. Per our running example, os.environ["NAME"] = "VALUE"
These environment variables can be accessed with "os.getenv('KEY')"

```python
if os.path.exists('.env'):
    print('Importing environment from .env file')
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]
```

## Config and `create_app`

Refer to `manage.py` for more details. 

```python
app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)
```

Currently the application will
look for an environment variable called `FLASK_CONFIG` or it will
move to the 'default' configuration which is the DevelopmentConfig
(again see `manage.py` for full details). Next it will call the
`create_app` method found in `app/__init__.py`. This method takes in a
name of a configuration and finds the configuration settings in
config.py. In heroku this will be set to 'production' i.e.
ProductionConfig. 

Next a `Manager` instance is created. Manager
is basically a nice plugin(?) that will allow us to get some useful
feedback when we call `manage.py` from the command line. It also handles
all the `manage.py` commands. The `@manager.command` and `@manager.option(...)`
decorators are used to determine what the help output should be
on the terminal. Migrate is used to make migration between db instances
really easy. Additionally `@manager.command` creates an application
context for use of plugins that are usually tied to the app.

## Make Shell Context

```python
def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)

manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)
```

Make shell context doesn't really serve a ton of purpose in most of our
development at h4i. However, it is entirely possible to explore the database
from the command line with this as seen in the lines above.


It is possible to create a general app shell or database specific shell.
For example doing 'python manage.py shell'

```sh
$ me = User()
$ db.session.add(me) && db.session.commit()
$ me.id
>> 1
```

This basically creates a new user object, commits it to the database gives
it an id. The db specific shell exposes the native MigrateCommands...
honestly you won't have to worry about these and future info can
be found the Flask-Migrate documentation.

## Recreate db

```python
@manager.command
def recreate_db():
    """
    Recreates a local database. You probably should not use this on
    production. EDIT: SHOULD NOT USE THIS IN PRODUCTION!!!
    """
    db.drop_all()
    db.create_all()
    db.session.commit()
```

So this will clear out all the user data (drop_all), will create a new
database but with all the tables and columns set up per your models.
create_all() and drop_all() rely upon the fact that you have imported
** ALL YOUR DATABASE MODELS **. If you are seeing some table not being
created this is the most likely culprit.

## Run Worker + Redis

The run_worker command will initialize a task queue. This is basically a
list of operations stored in memory that the server will get around to doing
eventually. This is great for doing asynchronous tasks. The memory store
used for holding these tasks is called Redis. We set up a default redis
password and then open a connection to the redis DB. We instantiate a worker
and add a queue of items that needs to be processed on that worker.

```
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
```

## Misc


You may/may not know this but the whole
`if __name__ == '__main__'` check is to see if this file is being executed
directly rather than indirectly (by being imported through another file).
So when we execute this file directly (by running python manage.py SOMECMD)
we get the option of instatiating the manager instance
These methods should be accessible from other
files though if imported. << HAVE NOT TESTED THIS THEORY OUT
But you would have a tough time executing these commands from cmd line
without the Manager init (otherwise you have to deal with argvs and
stuff that is frankly tedious).
