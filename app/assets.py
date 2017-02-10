from flask_assets import Bundle

app_css = Bundle('app.scss', filters='scss', output='styles/app.css')

app_js = Bundle('app.js', filters='jsmin', output='scripts/app.js')

vendor_css = Bundle('vendor/semantic.min.css', output='styles/vendor.css')

vendor_js = Bundle(
    'vendor/jquery.min.js',
    'vendor/semantic.min.js',
    'vendor/tablesort.min.js',
    'vendor/zxcvbn.js',
    filters='jsmin',
    output='scripts/vendor.js')
