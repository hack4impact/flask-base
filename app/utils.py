from redis import Redis
from flask import url_for, current_app
from rq_scheduler import Scheduler


def register_template_utils(app):
    """Register Jinja 2 helpers (called from __init__.py)."""

    @app.template_test()
    def equalto(value, other):
        return value == other

    @app.template_global()
    def is_hidden_field(field):
        from wtforms.fields import HiddenField
        return isinstance(field, HiddenField)

    app.add_template_global(index_for_role)


def index_for_role(role):
    return url_for(role.index)


def get_rq_scheduler(app=current_app):
    conn = Redis(
        host=app.config['RQ_DEFAULT_HOST'],
        port=app.config['RQ_DEFAULT_PORT'],
        db=0,
        password=app.config['RQ_DEFAULT_PASSWORD']
    )
    return Scheduler(connection=conn)  # Get a scheduler for the default queue
