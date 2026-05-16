# Configuration file for the Sphinx documentation builder.

project = "{{PROJECT}}"
author = "{{AUTHOR}}"
copyright = "{{YEAR}}, {{AUTHOR}}"

extensions = ["myst_parser", "sphinx_oceanid"]

myst_enable_extensions = ["colon_fence", "deflist"]

language = "ja"

templates_path = ["_templates"]

exclude_patterns = ["_build", "_templates", "Thumbs.db", ".DS_Store"]

html_theme = "shibuya"

html_theme_options = {"color_mode": "light"}

html_static_path = ["_static"]
