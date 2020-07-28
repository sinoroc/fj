#

"""Pip extensions."""

from __future__ import annotations

import logging
import typing

from .. import lib
from .. import _utils

if typing.TYPE_CHECKING:
    import pathlib

LOGGER = logging.getLogger(__name__)


class PipInstaller(lib.base.Installer):
    """Installer based on 'pip'."""

    def install_path(
            self,
            registry: lib.base.Registry,
            path: pathlib.Path,
            editable: bool = False,
    ) -> bool:
        """Install from local path."""
        #
        LOGGER.info("install_path(%s, editable=%s)", path, editable)
        #
        is_installed = False
        #
        purelib_dir_path = registry.environment.purelib_dir_path
        _utils.pip_wrapper.install(
            str(path),
            target_dir_path=purelib_dir_path,
            editable=editable,
        )
        #
        is_installed = True
        #
        return is_installed

    def install_requirement(
            self,
            registry: lib.base.Registry,
            requirement: lib.base.Requirement,
            target_dir_path: pathlib.Path,
    ) -> bool:
        """Install locked requirement with pip."""
        #
        LOGGER.info(
            "install_requirement(%s, %s)",
            requirement,
            target_dir_path,
        )
        #
        is_installed = False
        #
        interpreter_dir_path = registry.get_interpreter_dir_path()
        venv_dir_path = interpreter_dir_path.joinpath('pip_venv')
        venv_context = _utils.venv_wrapper.create_venv(venv_dir_path)
        #
        if venv_context:
            requirement_str = None
            #
            if requirement.url:
                requirement_str = requirement.url
            else:
                requirement_str = str(requirement)
            #
            _utils.pip_wrapper.install(
                requirement_str,
                target_dir_path,
                venv_context,
            )
            #
            is_installed = True
        #
        return is_installed


# EOF
