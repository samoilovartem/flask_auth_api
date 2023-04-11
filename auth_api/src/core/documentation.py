from apispec import APISpec
from flask import Flask


def load_spec(app: Flask, spec: APISpec):
    """Load routes, define schemes"""

    with app.app_context():

        # for _ in app.url_map.iter_rules():
        #     if _.endpoint in ('static', 'security.static'):
        #         continue
        #     print(_)
        #     print(dir(_))
        #
        #     # тоже чт и fn_name
        #     print(_.endpoint)
        #     # Rule bind c GET
        #     print(dir(_.build))
        #     # Аргументы функции
        #     print(_.build.__func__.__annotations__)
        #     # Докстринга функции
        #     print(_.build.__func__.__doc__)
        #     # Методы Доступные, 1й GET
        #     print(_.methods)
        #     # Ссылка от хоста
        #     print(_.rule)
        #     break

        for fn_name in app.view_functions:
            if fn_name in ('static', 'security.static'):
                continue
            view_fn = app.view_functions[fn_name]
            if view_fn.__doc__:
                spec.path(view=view_fn)
