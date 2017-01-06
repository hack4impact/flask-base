# Templating

This will cover various methods used in our jinja templates.

## `Base.html`

{% import 'macros/nav_macros.html' as nav %}

```html
<!DOCTYPE html>
<html>
    <head>
        {% include 'partials/_head.html' %}
        {# Any templates that extend this template can set custom_head_tags to add scripts to their page #}
        {% block custom_head_tags %}{% endblock %}
    </head>
    <body>
      {# Example dropdown menu setup. Uncomment lines to view
        {% set dropdown = 
          [
            ('account stuff',
              [
                ('account.login', 'login', 'sign in'),
                ('account.logout', 'logout', 'sign out'),
                ('2nd drop', [
                  ('account.login', 'login 2', ''),
                  ('3rd drop', [
                    ('main.index', 'home 2', '')
                  ])
                ])
              ]
            ),
            ('main.index', 'home 1', 'home')
          ]
        %}
      #}

        {% block nav %}
          {# add dropdown variable here to the render_nav method to render dropdowns #}
          {{ nav.render_nav(current_user) }}
        {% endblock %}

        {% include 'partials/_flashes.html' %}
        {# When extended, the content block contains all the html of the webpage #}
        {% block content %}
        {% endblock %}

        {# Implement CSRF protection for site #}
        {% if csrf_token() %}
            <div style="visibility: hidden; display: none">
                <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
            </div>
        {% endif %}
    </body>
</html>
```

## Macros: Password Strength (`check_password.html`)

Refer to `app/templates/macros/check_password.html`

This uses the zcvbn password checker to check the entropy of the password provided in the password field.
   Given a specified field, the password checker will check the entropy of the field and disable the submit
   button until the give 'level' is surpassed

## Macros: Form rendering (`render_form`)

```jinja
{% macro render_form(form, method='POST', extra_classes='', enctype=None) %}
    {% set flashes = {
        'error':   get_flashed_messages(category_filter=['form-error']),
        'warning': get_flashed_messages(category_filter=['form-check-email']),
        'info':    get_flashed_messages(category_filter=['form-info']),
        'success': get_flashed_messages(category_filter=['form-success'])
    } %}

    {{ begin_form(form, flashes, method=method, extra_classes=extra_classes, enctype=enctype) }}
        {% for field in form if not (is_hidden_field(field) or field.type == 'SubmitField') %}
            {{ render_form_field(field) }}
        {% endfor %}

        {{ form_message(flashes['error'], header='Something went wrong.', class='error') }}
        {{ form_message(flashes['warning'], header='Check your email.', class='warning') }}
        {{ form_message(flashes['info'], header='Information', class='info') }}
        {{ form_message(flashes['success'], header='Success!', class='success') }}

        {% for field in form | selectattr('type', 'equalto', 'SubmitField') %}
            {{ render_form_field(field) }}
        {% endfor %}
    {{ end_form(form) }}
{% endmacro %}
```
Render a flask.ext.wtforms.Form object.

```
Parameters:
    form          – The form to output.
    method        – <form> method attribute (default 'POST')
    extra_classes – The classes to add to the <form>.
    enctype       – <form> enctype attribute. If None, will automatically be set to
                    multipart/form-data if a FileField is present in the form. 
```

   Render Form renders a form object. It calls the begin form macro. Initially
   a 'flashes' variable is set with 'error', 'warning', 'info', 'success' which
   have values gathered from the get_flashed_messages method from flask. Note
   that all flashes are stored in SESSIOn with a category type. For most of our
   purposes, we only have form-error and form-success as our flash types (the
   second parameter in the flash function call seen in the views. 

   Then the begin_form macro is called and for each form field in the provided
   form render_form_field macro is called with the field. 
   All hidden fields (i.e. the CSRF field) and all submit fields is not rendered
   at this fime in render_form_field. In the render_form_field
   method, render_form_input is called for each input in the form field.

   After that, the form_message macro is called with each of the flash types.

   Lastly, the submit field is rendered. And the form is closed with the end_form
   macro

## Macros: Start Form (`begin_form`)

Set up the form, including hidden fields and error states.
begin_form is called from render_form. First a check is performed to check
if there exists a field within the form with type equal to FileField. This 
check is performed via filter ("|") in Jinja. This initial check produces a
filtered object, the 'list' filter creates a iterable list which we can then
check the length of with 'length > 0'. So if this check passes, then the enctype
must be set to multipart/form-data to accomodate a file upload. Otherwise, there
is no enctype.

Then the form tag is created with a method default of POST, enctype decided by the
check explained above. If there are errors (by field specific validator errors or 
if the flashes.error, flashes.warning, flashes.info, flashes.success is not None, 
then that class is added to the overall class of the form (along with any specified
extra_classes, default = ''). 

Lastly the hidden_tags are rendered. WTForms includes in this method the rendering of
the hidden CSRF field. We don't have to worry about that. 

Example output:

```html
<form action="" method="POST" enctype="multipart/form-data" class="ui form">
  <div style="display:none;">
    <input id="csrf_token" name="csrf_token" type="hidden" value="SOME_CSRF_TOKEN_HERE"> 
```

## Macros: Flash message to Form (`form_message`)

Render a message for the form. This is called from the render_form macro.

Recall the get_flashed_messages method. It will get the flash message from
the SESSION object with a given cateogory_filter. Within the render_form 
macro, the flashes variable is set with attributes 'errors', 'success',
'info', and 'warning'. The messages parameter for form_message contains the
flash messages for the respective attribute specified in flashes['some_attr'].

The form_message macro is called after all form fields have been rendered,
except for the Submit field. A div is created with class= 'ui CLASS message'
class being either error, success, info, or warning. This div is only created
if there are messages for a given flashes type! For each of the messages in
the flashes type, the message is filtered to only contain escaped HTML chars
and appended within the div ul as a list element.

Example Output:

```html
<div class="ui error message">
  <div class="header">Something went wrong.</div>
  <ul class="list">
    <li>Invalid email or password.</li>
  </ul>
</div>
```

## Macros: Render a form field (`render_form_field`)

Render a field for the form. This is rather self explanatory.
 If the field is 
   a radio field (RadioField WTForms object) extra_classes has an added class of
   'grouped fields' since all the options of a Radio Field must be styled in this
   way to display together.
   If there is a validation error on the form field, a error class is added to the
   field div (to make the field colored red). Then the render_form_input macro is 
   called with field object itself as a parameter. Any validation errors are then
   added with a sub-dev with content field.errors (we only show the first validation
   error for the given error for simplicity) and filter for HTML safe chars.

## Partials: `_flashes`

See the macros/form_macros for extended explanation of the 
   get_flashed_messages(category_filter) method. This macro renders
   general flash methods that appear at the top of the page. We render
   by flash type and create a separate 'ui {{ class }} message' div
   for each message within a specific flash type. Error = red,
   warning = yellow, info = blue, success = green.

## Partials: `_head`

This method contains all the assett imports (i.e. imports for scripts and styles for the app)
   Note that the asssets will be contained in the static/webassets-external folder when the app
   is in debug mode.