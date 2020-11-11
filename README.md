# flask-base
[![Circle CI](https://circleci.com/gh/hack4impact/flask-base.svg?style=svg)](https://circleci.com/gh/hack4impact/flask-base) 
[![Code Climate](https://codeclimate.com/github/hack4impact/flask-base/badges/gpa.svg)](https://codeclimate.com/github/hack4impact/flask-base/coverage)
[![Issue Count](https://codeclimate.com/github/hack4impact/flask-base/badges/issue_count.svg)](https://codeclimate.com/github/hack4impact/flask-base) ![python3.x](https://img.shields.io/badge/python-3.x-brightgreen.svg)  ![python2.x](https://img.shields.io/badge/python-2.x-yellow.svg)

![flask-base](readme_media/logo.png)

A Flask application template with the boilerplate code already done for you.


**Documentation available at [http://hack4impact.github.io/flask-base](http://hack4impact.github.io/flask-base).**

## What's included?

* Blueprints
* User and permissions management
* Flask-SQLAlchemy for databases
* Flask-WTF for forms
* Flask-Assets for asset management and SCSS compilation
* Flask-Mail for sending emails
* gzip compression
* Redis Queue for handling asynchronous tasks
* ZXCVBN password strength checker
* CKEditor for editing pages

## Demos

Home Page:

![home](readme_media/home.gif "home")

Registering User:

![registering](readme_media/register.gif "register")

Admin Editing Page:

![edit page](readme_media/editpage.gif "editpage")

Admin Editing Users:

![edit user](readme_media/edituser.gif "edituser")


## Setting up

##### Create your own repository from this Template

Navigate to the [main project page](https://github.com/hack4impact/flask-base) and click the big, green "Use this template" button at the top right of the page. Give your new repository a name and save it.

##### Clone the repository 

```
$ git clone https://github.com/YOUR_USERNAME/REPO_NAME.git
$ cd REPO_NAME
```

##### Initialize a virtual environment

Windows:
```
$ python3 -m venv venv
$ venv\Scripts\activate.bat
```

Unix/MacOS:
```
$ python3 -m venv venv
$ source venv/bin/activate
```
Learn more in [the documentation](https://docs.python.org/3/library/venv.html#creating-virtual-environments).

Note: if you are using a python before 3.3, it doesn't come with venv. Install [virtualenv](https://docs.python-guide.org/dev/virtualenvs/#lower-level-virtualenv) with pip instead.

##### (If you're on a Mac) Make sure xcode tools are installed

```
$ xcode-select --install
```

##### Add Environment Variables

Create a file called `config.env` that contains environment variables. **Very important: do not include the `config.env` file in any commits. This should remain private.** You will manually maintain this file locally, and keep it in sync on your host.

Variables declared in file have the following format: `ENVIRONMENT_VARIABLE=value`. You may also wrap values in double quotes like `ENVIRONMENT_VARIABLE="value with spaces"`.

1. In order for Flask to run, there must be a `SECRET_KEY` variable declared. Generating one is simple with Python 3:

   ```
   $ python3 -c "import secrets; print(secrets.token_hex(16))"
   ```

   This will give you a 32-character string. Copy this string and add it to your `config.env`:

   ```
   SECRET_KEY=Generated_Random_String
   ```

2. The mailing environment variables can be set as the following.
   We recommend using [Sendgrid](https://sendgrid.com) for a mailing SMTP server, but anything else will work as well.

   ```
   MAIL_USERNAME=SendgridUsername
   MAIL_PASSWORD=SendgridPassword
   ```

Other useful variables include:

| Variable        | Default   | Discussion  |
| --------------- |-------------| -----|
| `ADMIN_EMAIL`   | `flask-base-admin@example.com` | email for your first admin account |
| `ADMIN_PASSWORD`| `password`                     | password for your first admin account |
| `DATABASE_URL`  | `data-dev.sqlite`              | Database URL. Can be Postgres, sqlite, etc. |
| `REDISTOGO_URL` | `http://localhost:6379`        | [Redis To Go](https://redistogo.com) URL or any redis server url |
| `RAYGUN_APIKEY` | `None`                         | API key for [Raygun](https://raygun.com/raygun-providers/python), a crash and performance monitoring service |
| `FLASK_CONFIG`  | `default`                      | can be `development`, `production`, `default`, `heroku`, `unix`, or `testing`. Most of the time you will use `development` or `production`. |


##### Install the dependencies

```
$ pip install -r requirements.txt
```

##### Other dependencies for running locally

You need [Redis](http://redis.io/), and [Sass](http://sass-lang.com/). Chances are, these commands will work:


**Sass:**

```
$ gem install sass
```

**Redis:**

_Mac (using [homebrew](http://brew.sh/)):_

```
$ brew install redis
```

_Linux:_

```
$ sudo apt-get install redis-server
```

You will also need to install **PostgresQL**

_Mac (using homebrew):_

```
brew install postgresql
```

_Linux (based on this [issue](https://github.com/hack4impact/flask-base/issues/96)):_

```
sudo apt-get install libpq-dev
```


##### Create the database

```
$ python manage.py recreate_db
```

##### Other setup (e.g. creating roles in database)

```
$ python manage.py setup_dev
```

Note that this will create an admin user with email and password specified by the `ADMIN_EMAIL` and `ADMIN_PASSWORD` config variables. If not specified, they are both `flask-base-admin@example.com` and `password` respectively.

##### [Optional] Add fake data to the database

```
$ python manage.py add_fake_data
```

## Running the app

```
$ source env/bin/activate
$ honcho start -e config.env -f Local
```

For Windows users having issues with binding to a redis port locally, refer to [this issue](https://github.com/hack4impact/flask-base/issues/132).

## Gettin up and running with Docker and docker-compose:

##### Clone the repository 
```
$ git clone https://github.com/YOUR_USERNAME/REPO_NAME.git
$ cd REPO_NAME
```
##### Create and run the images:

```
$ docker-compose up
```

##### Create database and initial data for development:

```
$ docker-compose exec server ./init_database.sh
```

It will deploy 5 docker images:

- server: Flask app running in [http://localhost:5000](http://localhost:5000).
- worker: Worker ready to get tasks.
- postgres: Postgres SQL isolated from the app.
- adminer: Web client for database management, running in [http://localhost:8080](http://localhost:8080).
- redis: Redis SQL isolated from the app


## Formatting code

Before you submit changes to flask-base, you may want to autoformat your code with `python manage.py format`.


## Contributing

Contributions are welcome! Please refer to our [Code of Conduct](./CONDUCT.md) for more information.

## Documentation Changes

To make changes to the documentation refer to the [Mkdocs documentation](http://www.mkdocs.org/#installation) for setup.

To create a new documentation page, add a file to the `docs/` directory and edit `mkdocs.yml` to reference the file.

When the new files are merged into `master` and pushed to github. Run `mkdocs gh-deploy` to update the online documentation.

## Related
https://medium.freecodecamp.com/how-we-got-a-2-year-old-repo-trending-on-github-in-just-48-hours-12151039d78b#.se9jwnfk5

## License
[MIT License](LICENSE.md)
