from flask import (
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask.ext.login import (
    current_user,
    login_required,
    login_user,
    logout_user,
)
from . import account
from .. import db
from ..email import send_email
from ..models import User
from .forms import (
    ChangeEmailForm,
    ChangePasswordForm,
    CreatePasswordForm,
    LoginForm,
    RegistrationForm,
    RequestResetPasswordForm,
    ResetPasswordForm
)

# All routes are decorated with the name of the associated Blueprint along
# with the .route prop with attributes of (name, methods=[]). For example
# @account.route('/login', method=['GET', 'POST']) creates a route accessible
# at yourdomain.com/account/login. This route can accept either POST or GET
# requests which is appropriate since there is a form associated with the
# login process. This form is loaded from the forms.py file (in this case
# the LoginForm() is loaded) and we then check if the form is valid
# (validate_on_submit) in that it is a valid POST request.
# We grab the form field named 'email' and query the User database for the
# user that has that email. Then we call the 'verify_password' method
# from the User class for this specific user instance and check the hashed
# password in the database against the password provided by the user which
# is hashed with the SECRET_KEY. If everything is fine, the Flask-login
# extendion performs a login_user action and sets the SESSION['user_id']
# equivalent to the user id provided from the user instance. If the
# form has remember_me set to True (ie checked) then that is passed along
# as a parameter in login_user.
# If was redirected to this /login page, their URL will have a parameter
# called 'next' containing the URL they need to be directed to after they
# login. Otherwise, they will just be sent to the main.index route
# This is true for the admin as well. It is best to edit this functionality
# since index pages should differ by user type. There is a flash sent as well
# if the request is successful.
# If there is an error in the user checking process, then the user is kicked
# back to the account/login page with a flashed form error.
# If this is a GET request, only the account/login page is rendered


@account.route('/login', methods=['GET', 'POST'])
def login():
    """Log in an existing user."""
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            flash('You are now logged in. Welcome back!', 'success')
            return redirect(request.args.get('next') or url_for('main.index'))
        else:
            flash('Invalid email or password.', 'form-error')
    return render_template('account/login.html', form=form)

# This route is self explanatory. When the user fills the Registration form
# then a user object is created and added into the database. A new
# confirmation token is then generated and send an email to the new user
# with the added kwargs user and token for formatting purposes. The user
# is then redirected to the main index (but not logged in). otherwise, the
# account/register.html template is rendered.


@account.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user, and send them a confirmation email."""
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    email=form.email.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                   'account/email/confirm', user=user, token=token)
        flash('A confirmation link has been sent to {}.'.format(user.email),
              'warning')
        return redirect(url_for('main.index'))
    return render_template('account/register.html', form=form)

# The Flask-login Manager has a built in logout_user function that
# removes the SESSION variables from the user's browser and logs out
# the user completely


@account.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@account.route('/manage', methods=['GET', 'POST'])
@account.route('/manage/info', methods=['GET', 'POST'])
@login_required
def manage():
    """Display a user's account information."""
    return render_template('account/manage.html', user=current_user, form=None)

# This is also rather self explanatory. Note that this is
# the reset-password route used if the user cannot remember
# the password to log in. If the current user is logged in
# the user is redirected to their main index since users
# could just change their password on the manage/change-password
# route. After the form is validated, we check to see if
# a user exists, if so then a user is sent an email (otherwise
# no email is sent). Regardless, a flash is created saying that
# the email was sent.


@account.route('/reset-password', methods=['GET', 'POST'])
def reset_password_request():
    """Respond to existing user's request to reset their password."""
    if not current_user.is_anonymous():
        return redirect(url_for('main.index'))
    form = RequestResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_password_reset_token()
            send_email(user.email,
                       'Reset Your Password',
                       'account/email/reset_password',
                       user=user,
                       token=token,
                       next=request.args.get('next'))
        flash('A password reset link has been sent to {}.'
              .format(form.email.data),
              'warning')
        return redirect(url_for('account.login'))
    return render_template('account/reset_password.html', form=form)

# This route is a variation of the previous route in that it renders a
# ResetPasswordForm isntead of a RequestResetPasswordForm. It takes in
# a token and the form itself has an email field with a password reset
# field as well. If the email address is invalid, the user is kicked to
# main.index. Otherwise if the password reset request is valid (ie token
# is valid and email is valid) then the user is directed to the account
# login page. Else the user is sent to the main index as the token is invalid
# in this case.


@account.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset an existing user's password."""
    if not current_user.is_anonymous():
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash('Invalid email address.', 'form-error')
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.new_password.data):
            flash('Your password has been updated.', 'form-success')
            return redirect(url_for('account.login'))
        else:
            flash('The password reset link is invalid or has expired.',
                  'form-error')
            return redirect(url_for('main.index'))
    return render_template('account/reset_password.html', form=form)

# The change-password route is under the manage menu for a user and
# checks to see if the user has the correct old password in the provided
# field and then resets the password to the new field with the setter
# method specified in the user class.


@account.route('/manage/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change an existing user's password."""
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.new_password.data
            db.session.add(current_user)
            db.session.commit()
            flash('Your password has been updated.', 'form-success')
            return redirect(url_for('main.index'))
        else:
            flash('Original password is invalid.', 'form-error')
    return render_template('account/manage.html', form=form)

# This is very similar to the change-password manage route except that
# there is an email sent to the user's new email address with a token
# to confirm that the email address is valid. A password check is performed
# with the provided password in the form field to make sure that the
# request is authenticated.


@account.route('/manage/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    """Respond to existing user's request to change their email."""
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email,
                       'Confirm Your New Email',
                       'account/email/change_email',
                       user=current_user,
                       token=token)
            flash('A confirmation link has been sent to {}.'.format(new_email),
                  'warning')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.', 'form-error')
    return render_template('account/manage.html', form=form)

# very similar to some of the above methods for token verification


@account.route('/manage/change-email/<token>', methods=['GET', 'POST'])
@login_required
def change_email(token):
    """Change existing user's email with provided token."""
    if current_user.change_email(token):
        flash('Your email address has been updated.', 'success')
    else:
        flash('The confirmation link is invalid or has expired.', 'error')
    return redirect(url_for('main.index'))

# The route is triggered when the user clicks the 'resend confimration-email'
# button when they first log into their account without having
# confirmed their account.


@account.route('/confirm-account')
@login_required
def confirm_request():
    """Respond to new user's request to confirm their account."""
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'account/email/confirm', user=current_user, token=token)
    flash('A new confirmation link has been sent to {}.'.
          format(current_user.email),
          'warning')
    return redirect(url_for('main.index'))


@account.route('/confirm-account/<token>')
@login_required
def confirm(token):
    """Confirm new user's account with provided token."""
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm_account(token):
        flash('Your account has been confirmed.', 'success')
    else:
        flash('The confirmation link is invalid or has expired.', 'error')
    return redirect(url_for('main.index'))

# This route is used when an administrator invites a user to
# the system. If the user is authenticated already then they are
# kicked to the main index. Otherwise, we query the User table
# for the user_id (the form submission on the admin end creates
# a blank user record with just an id and email). If the password
# is already set, we kick to the main index. Otherwise, we render
# the createPasswordForm() which adds a password to the user
# record. If this is a GET requset, the user is invited to join
# via an email sent to them.


@account.route('/join-from-invite/<int:user_id>/<token>',
               methods=['GET', 'POST'])
def join_from_invite(user_id, token):
    """
    Confirm new user's account with provided token and prompt them to set
    a password.
    """
    if current_user is not None and current_user.is_authenticated():
        flash('You are already logged in.', 'error')
        return redirect(url_for('main.index'))

    new_user = User.query.get(user_id)
    if new_user is None:
        return redirect(404)

    if new_user.password_hash is not None:
        flash('You have already joined.', 'error')
        return redirect(url_for('main.index'))

    if new_user.confirm_account(token):
            form = CreatePasswordForm()
            if form.validate_on_submit():
                new_user.password = form.password.data
                db.session.add(new_user)
                db.session.commit()
                flash('Your password has been set. After you log in, you can '
                      'go to the "Your Account" page to review your account '
                      'information and settings.', 'success')
                return redirect(url_for('account.login'))
            return render_template('account/join_invite.html', form=form)
    else:
        flash('The confirmation link is invalid or has expired. Another '
              'invite email with a new link has been sent to you.', 'error')
        token = new_user.generate_confirmation_token()
        send_email(new_user.email,
                   'You Are Invited To Join',
                   'account/email/invite',
                   user=new_user,
                   user_id=new_user.id,
                   token=token)
    return redirect(url_for('main.index'))


@account.before_app_request
def before_request():
    """Force user to confirm email before accessing login-required routes."""
    if current_user.is_authenticated() \
            and not current_user.confirmed \
            and request.endpoint[:8] != 'account.' \
            and request.endpoint != 'static':
        return redirect(url_for('account.unconfirmed'))


@account.route('/unconfirmed')
def unconfirmed():
    """Catch users with unconfirmed emails."""
    if current_user.is_anonymous() or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('account/unconfirmed.html')
