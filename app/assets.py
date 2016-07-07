from flask.ext.assets import Bundle
# See app/__init__.py for details on this
# context is set as the assets/styles and
# assetts/scripts folders
# filter = scss -> convers .scss to css
# filter = jsmin -> converts to minified
#                   javascript

app_css = Bundle(
    '*.scss',
    filters='scss',
    output='styles/app.css'
)

app_js = Bundle(
    'app.js',
    filters='jsmin',
    output='scripts/app.js'
)

vendor_css = Bundle(
    'vendor/semantic.min.css',
    output='styles/vendor.css'
)

vendor_js = Bundle(
    'vendor/jquery.min.js',
    'vendor/semantic.min.js',
    'vendor/tablesort.min.js',
    filters='jsmin',
    output='scripts/vendor.js'
)
