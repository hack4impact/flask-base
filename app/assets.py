from flask.ext.assets import Bundle

app_css = Bundle('*.scss', filters='scss', output='styles/app.css')

app_js = Bundle('app.js', filters='jsmin', output='scripts/app.js')

vendor_css = Bundle('vendor/*.css', output='styles/vendor.css')

vendor_js = Bundle('vendor/*.js', filters='jsmin', output='scripts/vendor.js')
