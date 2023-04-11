from apispec import APISpec
from flask import Flask


def load_spec(app: Flask, spec: APISpec):
    """Load routes, define schemes"""

    with app.app_context():
        for fn_name in app.view_functions:
            if fn_name in ('static', 'security.static'):
                continue
            view_fn = app.view_functions[fn_name]
            if view_fn.__doc__:
                spec.path(view=view_fn)