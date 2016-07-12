from flask.ext.assets import Bundle
# See app/__init__.py for details on this
# context is set as the assets/styles and
# assetts/scripts folders
# filter = scss -> convers .scss to css
# filter = jsmin -> converts to minified
#                   javascript
# Bundle is just the plugin that helps us
# do this task.

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
    'vendor/*.css',
    output='styles/vendor.css'
)

vendor_js = Bundle(
    'vendor/*.js',
    filters='jsmin',
    output='scripts/vendor.js'
)
