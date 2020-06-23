#

"""Cache."""

from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    import pathlib
    #
    from . import _solver


def list_(registry: _solver.base.Registry) -> typing.List[pathlib.Path]:
    """List cached distributions."""
    #
    cached_distributions = []
    #
    distributions_cache_dir_path = registry.get_distributions_cache_dir_path()
    if distributions_cache_dir_path.is_dir():
        cached_distributions = [
            item
            for item
            in distributions_cache_dir_path.iterdir()
            if item.is_file()
        ]
    #
    return cached_distributions


# EOF
