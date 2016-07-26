from flask import Blueprint

# As with the other Blueprints, this will instantiate a Blueprint
# object and associate it with the variable account meaning that
# all the routes under this blueprint need to have the @account.route
# decorator. Since this is registered in app/__init__.py it needs to
# have all dependencies imported after the Blueprint is created.
#
# For an extended explanation of Blueprint refer to the app/__init__.py
# file

account = Blueprint('account', __name__)

from . import views  # noqa
