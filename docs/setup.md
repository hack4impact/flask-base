# Setting up

## Clone the repo

```
$ git clone https://github.com/hack4impact/flask-base.git
$ cd flask-base
```

## Initialize a virtualenv

```
$ pip install virtualenv
$ virtualenv -p /path/to/python3.x/installation env
$ source env/bin/activate
```

For mac users it will most likely be
```
$ pip install virtualenv
$ virtualenv -p python3 env
$ source env/bin/activate
```
Note: if you are using a python2.x version, point the -p value towards your python2.x path

## (If you're on a mac) Make sure xcode tools are installed

```
$ xcode-select --install
```

## Add Environment Variables 

Create a file called `.env` that contains environment variables in the following syntax: `ENVIRONMENT_VARIABLE=value`. For example,
the mailing environment variables can be set as the following
```
MAIL_USERNAME=example@domain.com
MAIL_PASSWORD=SuperSecretPassword
SECRET_KEY=SuperRandomStringToBeUsedForEncryption
```
**Note: do not include the `.env` file in any commits. This should remain private.**

## Install the dependencies

```
$ pip install -r requirements/common.txt
$ pip install -r requirements/dev.txt
```

## Other dependencies for running locally

Mac (using [homebrew](http://brew.sh/)):

```
$ brew install redis
```

Linux:

```
$ sudo apt-get install redis-server
```

## Create the database

```
$ python manage.py recreate_db
```

## Other setup (e.g. creating roles in database)

```
$ python manage.py setup_dev
```

Note that this will create an admin user with email and password specified by the `ADMIN_EMAIL` and `ADMIN_PASSWORD` config variables. If not specified, they are both `flask-base-admin@example.com` and `password` respectively.

## [Optional] Add fake data to the database

```
$ python manage.py add_fake_data
```

## [Optional. Only valid on `gulp-static-watcher` branch] Use gulp to live compile your files

* Install the Live Reload browser plugin from [here](http://livereload.com/)
* Run `npm install`
* Run `gulp`


## Running the app

```
$ source env/bin/activate
$ honcho start -f Local
```

