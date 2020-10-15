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
            target_dir_path: typing.Optional[pathlib.Path],
            editable: bool,
    ) -> bool:
        """Install from local path."""
        #
        LOGGER.info("install_path(%s, editable=%s)", path, editable)
        #
        is_installed = False
        #
        _utils.pip_wrapper.install(
            str(path),
            target_dir_path=target_dir_path,
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
                target_dir_path=target_dir_path,
                venv_context=venv_context,
            )
            #
            is_installed = True
        #
        return is_installed


class PipWheelBuilder(
        lib.base.WheelBuilder,
):  # pylint: disable=too-few-public-methods
    """Wheel builder based on 'pip'."""

    def build(
            self,
            registry: lib.base.Registry,
            source_dir_path: pathlib.Path,
            target_dir_path: pathlib.Path,
    ) -> typing.Optional[pathlib.Path]:
        """Implement."""
        #
        wheel_path = None
        #
        setup_py_file_path = source_dir_path.joinpath('setup.py')
        #
        if setup_py_file_path.is_file():
            _utils.pip_wrapper.wheel(source_dir_path, target_dir_path)
            for item in target_dir_path.glob('*.whl'):
                if item.is_file():
                    wheel_path = item
        #
        return wheel_path


# EOF
