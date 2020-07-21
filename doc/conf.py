#

"""Sphinx configuration."""

import importlib.metadata

_DISTRIBUTION_METADATA = importlib.metadata.metadata('fj')

_AUTHOR = _DISTRIBUTION_METADATA['Author']
_PROJECT = _DISTRIBUTION_METADATA['Name']
_VERSION = _DISTRIBUTION_METADATA['Version']

_MASTER_DOCUMENT = 'contents'

#
# Project
#

author = _AUTHOR
project = _PROJECT
release = _VERSION

extensions = []

#
# General
#

master_doc = _MASTER_DOCUMENT  # pylint: disable=invalid-name

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

# sphinxcontrib.autoprogram
extensions.append('sphinxcontrib.autoprogram')

# sphinx.ext.autodoc
extensions.append('sphinx.ext.autodoc')
autodoc_default_options = {
    'members': True,
}
autodoc_typehints = 'none'  # pylint: disable=invalid-name

# sphinx.ext.autosummary
extensions.append('sphinx.ext.autosummary')
autosummary_generate = True  # pylint: disable=invalid-name

# sphinx.ext.intersphinx
extensions.append('sphinx.ext.intersphinx')
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'tox': ('https://tox.readthedocs.io/en/stable/', None),
    'virtualenv': ('https://virtualenv.pypa.io/en/stable/', None),
}

# EOF
