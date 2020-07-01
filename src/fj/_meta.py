#

"""Meta information."""

import importlib.metadata

PROJECT_NAME = 'fj'

_DISTRIBUTION_METADATA = importlib.metadata.metadata(PROJECT_NAME)

SUMMARY = _DISTRIBUTION_METADATA['Summary']
VERSION = _DISTRIBUTION_METADATA['Version']


# EOF
