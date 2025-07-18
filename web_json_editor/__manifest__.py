{
    "name": "Web JSON Editor",
    "version": "1.0",
    "category": "Web",
    "summary": "JSON Editor widget for Odoo",
    "description": """
        Provides a reusable JSON Editor widget for Odoo with schema-based autocomplete.
        Features:
        - JSON syntax highlighting
        - Schema-based autocomplete
        - Multiple view modes (code, tree, form, view)
        - Validation
    """,
    "depends": [
        "web",
    ],
    "assets": {
        "web.assets_backend": [
            # Field widget
            "web_json_editor/static/src/fields/json_field.js",
            "web_json_editor/static/src/fields/json_field.xml",
            "web_json_editor/static/src/fields/json_field.scss",
        ],
    },
    "author": "Apexive Solutions LLC",
    "website": "https://github.com/apexive/odoo-llm",
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "LGPL-3",
}
