#Models

## `Permission` class

```
GENERAL = 0x01
ADMINISTER = 0xff
```
Okay so here is a seemingly simple piece of code I really think is
really cool! First of all we are setting up two enums here.
But they are set to weird hexadecimal numbers 0x01 and 0xff.
If you stick these into a hexadecimal -> decimal converter
you'll find that they represent 1 and 255 respectively. But
in binary they come out to 00000001 and 11111111 (8 ones).
If we do a binary and (&) on these two numbers, we can
actually get some unique properties from these.
So if we do GENERAL & ADMINSTER, it will come out to the following

```
  00000001
& 11111111
----------
  00000001
```

We get back the exact same value as GENERAL! Similarly if we do
ADMINSTER & GENERAL we get back GENERAL. This is useful for
checking user roles and who is exactly who in this system.
So we can create a method 'check(input, checker)' that will
take an input hex to test and one to text against. We only need
to do '(input & checker) == checker'. But there are some more
interesting applications for this. Let us define, for example,
a set of enums CAN_LIKE = 0x01, CAN_POST = 0x02, CAN_EDIT = 0x04
and CAN_REMOVE = 0x08. These are respectively in binary 00000001,
00000010, 00000100, 00001000. We can use binary OR (|) to create
composite user permissions e.g. CAN_LIKE | CAN_POST | CAN_EDIT =
0x07 = 00000111 -> NEW_ROLE. We can run 'check(NEW_ROLE, CAN_LIKE)'
or 'check(NEW_ROLE, CAN_POST)' or 'check(NEW_ROLE, CAN_EDIT)' and
all of these will return True.
For example NEW_ROLE & CAN_EDIT
```
  00000111
& 00000001
----------
  00000001 <- equivalent to CAN_EDIT enum
```
A function similar to the check described above can be found in
as the 'can' method below in the User class. Moving on!

## `Role` class

The Role class instatiates Role model. This is used for the
creation of users such as a general user and an administrator

### COLUMN DEFINITIONS:
`id` serves as the primary key (expects int).

`name` is the name of the role itself (expects unique String len 64)

`index` is the name of the index route for the route 

`default` is a T/F value that determines whether a new user created
  has that permission or note (ref insert_roles()). This is indexed
  meaning that a separate table has been created with default as the
  first column and id as the second column. Default in this table
  is sorted and a query for default performs a binary search rather
  than a linear search (reduces search time complexity from `O(N)` to
  `O(log n)`

`permissions` contains the permissions enum (see Permissions class)

`users` is not a column but it sets up a database relation. This case
  is a one-to-many relationship in that for ONE Role record, there are
  MANY associated User objects. The `backref` param specifies a
  bi-directional relationship between the two tables in that there is
  a new property on both a given Role and User object. E.g. Role.users
  will refer to the User object (i.e. the user table). and User.role
  (role being the string specified with backref) will refer to the
  Role object. Lazy = dynamic specifies to return a Query object
  instead of actually asking the relationship to load all of its child
  elements upon creating the relationship. It is best practice to
  include lazy=dynamic upon the establishment of a relationship.
###Sub-note on lazy-dynamic and backref:

 Currently, lazy-dynamic will
make the User collection to be loaded in as a Query object (so not
everything is loaded at once). Simiarly (as mentioned above), the
User object can reference the Role object by doing User.role however,
this uses the default collection loading behavior (i.e. load the entire
collection at once). It is fine in this case since the amount of
Roles in the Role collection will be *much* less than the amount of
entries in the User collection. However, we can specify that User.role
uses the lazy-dynamic loading scheme. Simply redefine users here to
```
users = db.relationship('User', backref=db.backref('role',
                                      lazy='dynamic'), lazy='dynamic')
```

### insert_roles() and SQLAlchemy Sessions

The staticmethod decorator specifies that insert_roles() must be
be called with a instance of the Role class. E.g. role_obj.insert_roles()
This method is fairly self-explanatory. It specifies a 'roles' dict
This is then iterated through and foreach role in the 'roles' dict
we check to see if it already exists (by name) in the Role object
i.e. the Roles table. If not, then a new Role object is instantiated
After that, the perms, index, default props are set and the the
role object is now added to the db session and then committed.

A note about sqlalchemy if you haven't noticed already: All changes
are added to a Session object (handled by SQLAlchemy). Unless specified
otherwise, the session object has a merge operation that finds the difs
between the new object (that was created and added to the session object)
and the currently existing (corresponding) object existing in the table
right now. Then a commit() propegates these changes into the database
making as little changes as possible (i.e. every time we update a
record, the record's attribute is changed 'in place' rather than being
deleted and then replaced. Neat :)

### `__repr__`

```python
def __repr__(self):
    return '<Role \'%s\'>' % self.name
```

this __repr__ method is pretty much optional, but it is helpful in that
it will allow the program to pretty print the user object when you come
across an error

## `User` Model

The class User represents users... it extends db.Model and
UserMixin. Per the flask-login documentation, the User class
needs to implement is_authenticated (returns True if the user is
authenticated and in turn fulfill login_required), is_active
(returns True if the user has been activated i.e. confirmed by
email in our case), is_anonymous (returns if a user is Anonymous
i.e. is_active = is_authenticated = False, is_anonymous = True,
and get_id() = None), get_id() (returns a UNICODE that has the
id of the user NOT an int).

### Column Descriptions:

`id` - primary key for the table. Id of the user. i.e. the
  unique identifier for the collection

`confirmed` - boolean val (default value = False) that is
  an indication of whether the user has confirmed their
  account via email.

`first_name` - ... string self explanatory

`last_name` - ... string self explanatory

`email` - string self explanatory. But we impose the uniqueness
  constraint on this column. It is necessary to check for this
  on the backend before entering an email into the table,
  else there will be some nasty errors produced when the user
  tries to add an existing email into the table.

Note: first_name, last_name, email form an index table for easy lookup. See Role for more info

`password_hash` is a 128 char long string containing the hashed
  password. As always, it is best practice to never include the
  plaintext password on the server. This hashed password is
  checked against when authenticating users.

`role_id` is the id of the role the user is. It is a foreign key
  and relates to the id's in the Role collection. By default
  the general user is role.id = 1, and role.id = 2 is the
  admin. Also note that we refer to the Role collection with
  'roles' rather than the assigned backref 'role' since we
  are referring to an individual column.

## Other User Class Variables and Methods
Note that the following methods are actually available in your Jinja
templates since they are attached to the user instance.

`full_name` provides the full name of the user given a first and last
  name

`can` provides a really cool way of determining whether a user has
  given permissions. See the Permissions class for more info.
`is_admin` is an implementation of `can` to test a user against
  admin permissions.

`password` This does not give a password if a user just
  calls the method and throws an AttributeError. However
  if someone chooses to set a password e.g.
  u = User( password = `test` ) the second definition of
  password method is run, taking the keyword arg (kwarg) as the
  password to then call the generate_password_hash method and
  set the password_hash property of the user to the generated
  password.

`verify_password` well...verifies a provided user plaintext password
  against the password_hash in the user record. Uses the
  check_password_hash method.

`generate_confirmation_token` returns a cryptographically signed
  string with encrypted user id under key `confirm`. This will
  expire in 7 days. Note that Serializer is actually
  TimedJSONWebSerializer when looking for documentation.

`generate_changed_email_token` also returns a cryptographically
  signed string with encrypted user id under key `change_email`
  and a encrypted new_email parameter password into the method
  containing the desired new email the user wants to replace the
  old email with.

`generate_password_reset_token` operates similarly to `generate_
  confirmation_token`. Generates token for password reset

NOTE: For context, the generate_..._token methods are used to create
a random string that will be later added to an email (usually) to the
requesting user.

### `confirm_account`
The confirm_account method will take in a token (which was presumably
generated from the generate_confirmation_token method) and then return
True if the provided token is valid (and can be decrypted with the
SECRET_KEY and has not expired) AND the decrypted token has the key
'confirm' with the id of the requesting user. If so, it flips the
'confirmed' attribute of the requesting user to True.
Will throw BadSignature of the token is invalid, will throw
SignatureExpired if the token is past the expiration time.

### `change_email`

The change_email method will take in a token (which was presumably
generated from the generate_email_token method) and then return True
True if the token is valid (see above method for explanation of 'valid')
and contains the key 'change_email' with value = user id in addition to
the key 'new_email' with the new email address the user wants to change
their email to. Before the new_email is committed to the session, a
query is performed on the User collection on all the emails to maintain
the unique constraint on the email columns. Then the user's 'email'
attribute is set to the 'new_email' specified in the decrypted token.
will throw BadSignature if invalid token and SignatureExpired if the
token is expired.

## AnonymousUser


We define a custom AnonymousUser class that represents a non-logged
user. It extends the AnonymousUserMixing provided by flask-loginmanager
we deny all permissions and affirm that this user is not an admin

```
class AnonymousUser(AnonymousUserMixin):
    def can(self, _):
        return False

    def is_admin(self):
        return False
```

```
login_manager.anonymous_user = AnonymousUser
```

We then register our custom AnonymousUser class as the default login_manager
anonymous user class



```
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
```
This is the default user_loader method for login_manager. This method
defines how to query for a user given a user_id from the user SESSION object.
It is pretty straightforward, it will query the User table and find the user
with ID equal to the user_id provided in the user SESSION

