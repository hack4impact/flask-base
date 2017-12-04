# Deployment

The aim of this guide is to walk you through launching our basic `flask-base` repository found [here](https://github.com/hack4impact.org/flask-base) and will also cover some common situations and issues encountered from previous projects.

## What is Heroku and Why are we using it?

To get started we are going to cover what heroku is and how to set it up. 

Just a little bit of background. Currently, when you run your app with `python manage.py runserver` or `honcho start -f Local` you are running on your computer only (on something like `localhost:5000`). Of course this means that if anyone tries to access your application, they will be stuck with a `404 not found` error. Thus we must put your application onto a publicly accessible computer that is constantly running. This is exactly what a server does. When you type in something like `hack4impact.org`, a request is first sent to a Domain Name Server or _DNS_ which then maps the domain name `hack4impact.org` to an IP Address which points to the server which then renders pages and serves them over to you, the client. Seems simple. But how do you get a server?

Heroku is the answer. The heroku platform is a cloud platform that runs your apps in containers called **dynos** and hosts these apps for free (...ish, we'll get to pricing later). These dynos can host apps and allow you to scale the applications infinitely (at a cost of course) to handle more traffic. Additionally, the heroku dynos contain all the code you need to run a python app from the get go and will install any pip dependencies. Your app lives in a remote git repository on heroku's servers. When you push to the remote heroku repository, heroku will merge the changes, reset your server, and run the new version of your app. Heroku makes this entire process seamless, so its super easy to maintain your app well after it has been launched.

Now that we have a good understanding of what heroku is and why we want to use it. Let's get started with launching the application to heroku!

## Basic Setup: Heroku Account and CLI Installation

Head over to [https://signup.heroku.com](https://signup.heroku.com) to set up an account. Once you are set up, confirm your email and set up your password.

Next, install the heroku command line interface (CLI) for your operating system at [https://devcenter.heroku.com/articles/heroku-cli](https://devcenter.heroku.com/articles/heroku-cli). 

## Heroku Dyno Creation and Initial Setup

Go to the directory containing the application you wish to launch. For demo purposes, we will be using the `flask-base` repository which you can clone from [https://www.github.com/hack4impact/flask-base](https://www.github.com/hack4impact/flask-base). This is a python application that has a SQLite database and a Redis Task Queue. 

Go to your terminal and type in `heroku login`. If you have set up everything correctly with the CLI installation in the previous section, you should be prompted for your Heroku account credentials (from the previous section as well). 

```sh
$ heroku login
Enter your Heroku credentials.
Email: adam@example.com
Password (typing will be hidden):
Authentication successful.
```
Before creating a heroku dyno, make sure you are at the root directory of your application. Next make sure your application is a git repository (you can do `git init` to make it one), and make sure the current git branch you are on is **master** since heroku only pushes changes from that branch. Also make sure that your `requirements.txt` file contains all the pip modules to work (you can do `pip freeze > requirements.txt` to place all your installed pip modules in `requirements.txt`).

To create the dyno, run in the terminal `heroku create <app-name>`. 

_Note that I use `<variable>` to indicate that the variable is optional and the carats should be excluded. E.g. a valid interpretation of the above would be `heroku create` or `heroku create myappname` but NOT `heroku create <myappname>`_. 

Heroku will create an empty dyno with name you specified with `app-name` or a random name which it will output to the terminal.

```sh
$ heroku create flask-base-demo
Creating ⬢ flask-base-demo... done
https://flask-base-demo.herokuapp.com/ | https://git.heroku.com/flask-base-demo.git
```

Your application will be accessible at _https://flask-base-demo.herokuapp.com_ (per the example above) and the remote github repository you push your code to is at `https://git.heroku.com/flask-base-demo.git`. 

Next we can run `git push heroku master`. This will push all your existing code to the heroku repository. Additionally, heroku will run commands found in your `Procfile` which has the following contents:

```txt
web: gunicorn manage:app
worker: python -u manage.py run_worker
```
This specifies that there is will be a `web` dyno (a server that serves pages to clients) and a `worker` dyno (in the case of flask-base, a server that handles methods equeued to the Redis task queue). 

If all goes well, you should see an output something similar to this:

```
Counting objects: 822, done.
Delta compression using up to 8 threads.
Compressing objects: 100% (339/339), done.
Writing objects: 100% (822/822), 1.12 MiB | 914.00 KiB/s, done.
Total 822 (delta 457), reused 822 (delta 457)
remote: Compressing source files... done.
remote: Building source:
remote:
remote: -----> Python app detected
remote: -----> Installing python-2.7.13
remote:      $ pip install -r requirements.txt
remote:        Collecting Flask==0.10.1 (from -r /tmp/.../requirements.txt (line 1))
...
...
...
remote:        Successfully installed Faker-0.7.3 Flask-0.10.1 Flask-Assets-0.10 Flask-Compress-1.2.1 Flask-Login-0.2.11 Flask-Mail-0.9.1 Flask-Migrate-1.4.0 Flask-RQ-0.2 Flask-SQLAlchemy-2.0 Flask-SSLify-0.1.5 Flask-Script-2.0.5 Flask-WTF-0.11 Jinja2-2.7.3 Mako-1.0.1 MarkupSafe-0.23 SQLAlchemy-1.0.6 WTForms-2.0.2 Werkzeug-0.10.4 alembic-0.7.6 blinker-1.3 click-6.6 gunicorn-19.3.0 ipaddress-1.0.17 itsdangerous-0.24 jsmin-2.1.6 jsonpickle-0.9.2 psycopg2-2.6.1 python-dateutil-2.6.0 raygun4py-3.0.2 redis-2.10.5 rq-0.5.6 six-1.10.0 webassets-0.10.1
remote:
remote: -----> Discovering process types
remote:        Procfile declares types -> web, worker
remote:
remote: -----> Compressing...
remote:        Done: 43.7M
remote: -----> Launching...
remote:        Released v4
remote:        https://flask-base-demo.herokuapp.com/ deployed to Heroku
remote:
remote: Verifying deploy... done.
To https://git.heroku.com/flask-base-demo.git
 * [new branch]      master -> master
```

## Configuration

Next we have to set up some configuration variables to ensure that the application will be in production mode.

From the command line run

```
heroku config:set FLASK_CONFIG=production
```

Also set your Sendgrid email credentials as configuration variables as well (if you want the application to send email)

```
heroku config:set MAIL_USERNAME=yourSendgridUsername MAIL_PASSWORD=yourSendgridPassword
```
Next you should add a `SECRET_KEY`

```
heroku config:set SECRET_KEY=SuperRandomLongStringToPreventDecryptionWithNumbers123456789
```

And also set, `SSL_DISABLE` to `False`

```
heroku config:set SSL_DISABLE=False
```

If you plan to use redis, go to [https://elements.heroku.com/addons/redistogo?app=flask-base-demo](https://elements.heroku.com/addons/redistogo?app=flask-base-demo) and follow the onscreen steps to provision a redis instance. 

Also if you have a Raygun API Key, add the config variable `RAYGUN_APIKEY` in a similar fashion  to above. This will enable error reporting.

## Database Creation & Launching

First run `heroku ps:scale web=1 worker=1`. You may need to add a credit card for this to work (it will notify you on the command line to do that).

Next run `heroku run python manage.py recreate_db` to create your database.

Lastly, run the command to add an admin user for you app. In flask base it will be the following `heroku run python manage.py setup_dev`. 

In general if you want to run a command on the app it will be in the format of `heroku run <full command here>`. Additionally you can access the file system with `heroku run bash`. 

You can now access your app at the URL from earlier and log in with the default user.

## Domain Name + HTTPS Setup

This guide encompasses all you need to get set up with SSL [https://support.cloudflare.com/hc/en-us/articles/205893698-Configure-CloudFlare-and-Heroku-over-HTTPS](https://support.cloudflare.com/hc/en-us/articles/205893698-Configure-CloudFlare-and-Heroku-over-HTTPS). 

## Debugging

`heroku logs --tail` will open up a running log of anything that happens on your heroku dyno. 

Additionally, if you have Raygun configured, you'll get error reports (otherwise, you can look at older versions of flask base where we sent errors to the main administrator email). 

Lastly, you can use an application like **[Postico](https://eggerapps.at/postico/)** to actually look at your database in production. To get the credentials for the application to work with Postico, do the following:

- Run `heroku config` to print out all configuration variables.

- Find the `DATABASE_URL` variable, it should look something like `postgres://blahblahblah:morerandomstuff123456@ec2-12-345-678-9.compute-1.amazonaws.com:5432/foobar`

- In Postico, click "New Favorite".

- For the fields use the following reference to interpret the parts of the `DATABASE_URL` variable: `postgres://User:Password@Host:Port/Database`

- If you want to view your redis queue, use the following web interface [https://www.redsmin.com/](https://www.redsmin.com/) or the command line.

## Heroku considerations, scaling and pricing

If your application uses file uploads, **Heroku does not have a persistent file system**, thus you need to set up a Amazon S3 Bucket to upload your file to. This heroku guide has a nice way to upload files with AJAX on the frontend [https://devcenter.heroku.com/articles/s3](https://devcenter.heroku.com/articles/s3). You can also view the [Reading Terminal Market](https://github.com/hack4impact/reading-terminal-market) Repo for an example of how to use file uploads

Heroku has a limit of 30 seconds on processing a request. This means that once a user submits a request to a URL Endpoint, a response must be sent back in 30 seconds, otherwise the request will abort and the user will get a timeout error. You should explore using a Redis queue to process requests in the background if they require more than a few seconds to run. Or you can issue AJAX requests on the frontend to a URL (at least this will just silently fail). 

Heroku postgresQL has a limit of about 10k rows. If your application will use more than that, then you should follow [this guide](https://devcenter.heroku.com/articles/upgrading-heroku-postgres-databases). 

Also you should upgrade your heroku instance to the `hobby` tier to ensure that it will be working 24 hrs. The free tier will only work 18 hrs a day and will _sleep_ the application after 5 minutes if inactive (meaning that it will take a while to start up again from a sleep state). You can change this on the heroku dashboard [https://dashboard.heroku.com/apps/](https://dashboard.heroku.com/apps/).
