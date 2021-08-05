import os
import sys

sys.path.insert(0, os.path.abspath("../../"))
import freiner

on_rtd = os.environ.get("READTHEDOCS", None) == "True"

if not on_rtd:  # only import and set the theme if we're building docs locally
    import sphinx_rtd_theme

    html_theme = "sphinx_rtd_theme"
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

autodoc_default_options = {
    "members": True,
    "show-inheritance": True,
}

autoclass_content = "both"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
]

source_suffix = ".rst"
master_doc = "index"
project = "Freiner"
copyright = "2021, Matthew Gamble"

version = release = freiner.__version__
exclude_patterns = []
pygments_style = "sphinx"
htmlhelp_basename = "freinerdoc"

latex_documents = [
    ("index", "limits.tex", "Freiner Documentation", "Matthew Gamble", "manual"),
]
man_pages = [("index", "freiner", "Freiner Documentation", ["Matthew Gamble"], 1)]

texinfo_documents = [
    (
        "index",
        "freiner",
        "Freiner Documentation",
        "Matthew Gamble",
        "freiner",
        "One line description of project.",
        "Miscellaneous",
    ),
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/", None),
    "redis": ("https://redis-py.readthedocs.io/", None),
    "rediscluster": ("https://redis-py-cluster.readthedocs.io/", None),
    "pymemcache": ("https://pymemcache.readthedocs.io/", None),
}
