#


"""Sphinx configuration."""

import importlib.metadata


_DISTRIBUTION_METADATA = importlib.metadata.metadata('fj')

_AUTHOR = _DISTRIBUTION_METADATA['Author']
_PROJECT = _DISTRIBUTION_METADATA['Name']
_SUMMARY = _DISTRIBUTION_METADATA['Summary']
_VERSION = _DISTRIBUTION_METADATA['Version']

_MASTER_DOCUMENT = 'contents'


#
# Project
#

author = _AUTHOR
project = _PROJECT
version = _VERSION

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinxcontrib.autoprogram',
]


#
# General
#

master_doc = _MASTER_DOCUMENT  # pylint: disable=invalid-name

templates_path = [
    '_templates',
]


#
# HTML
#

html_show_copyright = False  # pylint: disable=invalid-name

html_sidebars = {
    '**': [
        'globaltoc.html',
        'searchbox.html',
        'sourcelink.html',
    ],
}

html_theme = 'bizstyle'  # pylint: disable=invalid-name

html_use_index = False  # pylint: disable=invalid-name


#
# Extensions
#

# sphinx.ext.autosummary
autodoc_default_options = {
    'members': True,
}
autodoc_typehints = 'none'  # pylint: disable=invalid-name

# sphinx.ext.autosummary
autosummary_generate = True  # pylint: disable=invalid-name

# sphinx.ext.intersphinx
intersphinx_mapping = {
    'python': ('https://docs.python.org/', None),
    'tox': ('https://tox.readthedocs.io/en/stable/', None),
    'virtualenv': ('https://virtualenv.pypa.io/en/stable/', None),
}


# EOF
