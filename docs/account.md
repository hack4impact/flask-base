Routing (Account Routes)

This guide will be explaining the concept of routing by going through a file. We will be using `app/account/views.py`

## Login

```
@account.route('/login', methods=['GET', 'POST'])
def login():
    """Log in an existing user."""
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.password_hash is not None and \
                user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            flash('You are now logged in. Welcome back!', 'success')
            return redirect(request.args.get('next') or url_for('main.index'))
        else:
            flash('Invalid email or password.', 'form-error')
    return render_template('account/login.html', form=form)
```
All routes are decorated with the name of the associated Blueprint along
with the .route prop with attributes of (name, methods=[]). For example
`@account.route('/login', method=['GET', 'POST'])` creates a route accessible
at `yourdomain.com/account/login`.

This route can accept either `POST` or `GET`
requests which is appropriate since there is a form associated with the
login process. This form is loaded from the forms.py file (in this case
the `LoginForm()` is loaded) and we then check if the form is valid
(`validate_on_submit`) in that it is a valid POST request.
We grab the form field named 'email' and query the User database for the
user that has that email. Then we call the `verify_password` method
from the User class for this specific user instance and check the hashed
password in the database against the password provided by the user which
is hashed with the SECRET_KEY. If everything is fine, the Flask-login
extendion performs a login_user action and sets the `SESSION['user_id']`
equivalent to the user id provided from the user instance. If the
form has remember_me set to True (ie checked) then that is passed along
as a parameter in login_user.

If it was redirected to this /login page, their URL will have a parameter
called `next` containing the URL they need to be directed to after they
login. Otherwise, they will just be sent to the main.index route
This is true for the admin as well. It is best to edit this functionality
since index pages should differ by user type. There is a flash sent as well
if the request is successful.

If there is an error in the user checking process, then the user is kicked
back to the account/login page with a flashed form error.

If this is a GET request, only the account/login page is rendered

## Logout

```
@account.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))
```

The Flask-login Manager has a built in logout_user function that
removes the SESSION variables from the user's browser and logs out
the user completely

