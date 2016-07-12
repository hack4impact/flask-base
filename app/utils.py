from flask import url_for

from wtforms.fields import HiddenField


def register_template_utils(app):
    """Register Jinja 2 helpers (called from __init__.py)."""

    # the template_test decorator allows us to add tests for
    # conditional statements into jinja. For the test below,
    # {% if x is equalto y %} blah {% endif %}
    @app.template_test()
    def equalto(value, other):
        return value == other

    # This adds a global method. Can be accessed with
    # {{ is_hidden_field(field) }}
    @app.template_global()
    def is_hidden_field(field):
        return isinstance(field, HiddenField)

    # see below, but this will add another template global

    app.add_template_global(index_for_role)

# Provides the link to the index page for a created role...


def index_for_role(role):
    return url_for(role.index + '.index')
