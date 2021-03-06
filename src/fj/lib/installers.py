#

"""Installers."""

from __future__ import annotations

import logging
import typing

LOGGER = logging.getLogger(__name__)

if typing.TYPE_CHECKING:
    import pathlib
    #
    from . import base


def install_path(
        registry: base.Registry,
        path: pathlib.Path,
        target_dir_path: typing.Optional[pathlib.Path] = None,
        editable: bool = False,
) -> bool:
    """Install from local path."""
    #
    is_installed = False
    #
    if target_dir_path is None:
        target_dir_path = registry.environment.purelib_dir_path
    #
    for installer in registry.installers:
        is_installed = installer.install_path(
            registry,
            path,
            target_dir_path,
            editable,
        )
        if is_installed:
            break
    #
    return is_installed


def install_requirement(
        registry: base.Registry,
        requirement: base.Requirement,
        target_dir_path: pathlib.Path,
) -> bool:
    """Install locked requirement."""
    is_installed = False
    for installer in registry.installers:
        is_installed = installer.install_requirement(
            registry,
            requirement,
            target_dir_path,
        )
        if is_installed:
            break
    return is_installed


# EOF
