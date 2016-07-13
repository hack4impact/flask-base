import os
import urlparse

# specify absolute path

basedir = os.path.abspath(os.path.dirname(__file__))

# So lets go through each of the configuring variables.
#
# APP_NAME is the name of the app. This is used in templating
# to make sure that all the pages at least have the same html
# title
#
# SECRET_KEY is a alpha-numeric string that is used for crypto
# related things in some parts of the application. Set it as an
# environment variable or default to our insecure one. This is
# used in password hashing see app/models/user.py for more info.
# YOU SHOULD SET THIS AS A CONFIG VAR IN PRODUCTION!!!!
#
# SQLALCHEMY_COMMIT_ON_TEARDOWN is used to auto-commit any sessions
# that are open at the end of the 'app context' or basically the
# current request on the application. But it is best practice
# to go ahead and commit after any db.session is created
#
# SSL_DISABLE I unfortunately do not know much about ;(. But something
# realated to https
#
# MAIL_... is used for basic mailing server connectivity throug the
# SMTP protocol. This is further described in email.py.


class Config:
    APP_NAME = 'Flask-Base'
    SECRET_KEY = os.environ.get('SECRET_KEY') or \
        'SECRET_KEY:YOU_SHOULD_NOT_SEE_THIS_IN_PRODUCTION'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SSL_DISABLE = True

    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    ADMIN_EMAIL = 'flask-base-admin@example.com'
    EMAIL_SUBJECT_PREFIX = '[{}]'.format(APP_NAME)
    EMAIL_SENDER = '{app_name} Admin <{email}>'.format(app_name=APP_NAME,
                                                       email=MAIL_USERNAME)

    REDIS_URL = os.getenv('REDISTOGO_URL') or 'http://localhost:6379'

    # Parse the REDIS_URL to set RQ config variables
    urlparse.uses_netloc.append('redis')
    url = urlparse.urlparse(REDIS_URL)

    RQ_DEFAULT_HOST = url.hostname
    RQ_DEFAULT_PORT = url.port
    RQ_DEFAULT_PASSWORD = url.password
    RQ_DEFAULT_DB = 0

    @staticmethod
    def init_app(app):
        if os.environ.get('SECRET_KEY') is None:
            print Config.SECRET_KEY
        pass

# DevelopmentConfig will extend the Config class.
# It allows for the traditional Flask screen of death when
# there is an error in the application. It links the database
# to the data-dev.sqlite file in the flask-base directory


class DevelopmentConfig(Config):
    DEBUG = True
    ASSETS_DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

# Pretty much the same as above but with CSRF enabled


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')

    # normally the init_app method doesn't do anything, but in the
    # production environment, we send all errors to the registered
    # admin email

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        assert os.environ.get('SECRET_KEY'), 'SECRET_KEY IS NOT SET!'
        # Email errors to administators
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure = ()
        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.EMAIL_SENDER,
            toaddrs=[cls.ADMIN_EMAIL],
            subject=cls.EMAIL_SUBJECT_PREFIX + ' Application Error',
            credentials=credentials,
            secure=secure
        )
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)


class HerokuConfig(ProductionConfig):
    SSL_DISABLE = bool(os.environ.get('SSL_DISABLE'))

    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # Handle proxy server headers
        from werkzeug.contrib.fixers import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)


class UnixConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # Log to syslog
        import logging
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
