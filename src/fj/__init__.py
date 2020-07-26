#

"""Fj. Pool installations of Python projects."""

from . import _meta

try:  # pylint: disable=too-many-try-statements
    from . import ext
    from . import lib
except ModuleNotFoundError:
    _DEPENDENCIES_IMPORTED = False
else:
    _DEPENDENCIES_IMPORTED = True

__version__ = _meta.VERSION  # PEP 396

# EOF
