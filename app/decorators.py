from functools import wraps

from flask import abort
from flask.ext.login import current_user

from .models import Permission

# This is a rather complicated function, but the general idea
# is that it will allow is to create a decorator that will
# kick users to a 403 page if they dont have a certain permission
# or let them continue. First there is a permission_required
# method which takes in a permission e.g. Permission.ADMINISTER
# Then it create a function called 'decorator' which performs
# the check in a separate function itself decorates called
# 'decorated_function'. It returns the result from
# 'decorate_function' as well as the results from a specified
# parameter f that serves as an extra function call. The
# @wraps(f) decorator is itself used to give context for the
# decorated function and actually point that context towards
# the fully decorated function when the permission_required()
# decorator is invoked. Tl;dr it does some complicated stuff
# you don't really need to know about


def permission_required(permission):
    """Restrict a view to users with the given permission."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)
