#

"""Wrapper for pip."""

from __future__ import annotations

import logging
import subprocess
import sys
import typing

from . import _venv

if typing.TYPE_CHECKING:
    import pathlib
    #
    from . import _solver

LOGGER = logging.getLogger(__name__)


def _do_install(
        requirement_str: str,
        target_dir_path: typing.Optional[pathlib.Path] = None,
        venv_context: typing.Optional[_venv.VenvContext] = None,
        editable: bool = False,
) -> None:
    command = [
        venv_context.env_exe if venv_context else sys.executable,
        '-m',
        'pip',
        'install',
        '--no-deps',
    ]
    if target_dir_path:
        command.extend(
            [
                '--target',
                str(target_dir_path),
            ],
        )
    if editable:
        command.append('--editable')
    command.append(requirement_str)
    LOGGER.info("_do_install %s", command)
    subprocess.check_call(command)


def install_path(
        registry: _solver.base.Registry,
        path: pathlib.Path,
        editable: bool = False,
) -> None:
    """Install from local path."""
    LOGGER.info("install_path(%s, editable=%s)", path, editable)
    purelib_dir_path = registry.environment.purelib_dir_path
    _do_install(str(path), target_dir_path=purelib_dir_path, editable=editable)


def install_requirement(
        registry: _solver.base.Registry,
        requirement: _solver.base.Requirement,
        target_dir_path: pathlib.Path,
) -> None:
    """Install locked requirement with pip."""
    LOGGER.info("install_requirement(%s, %s)", requirement, target_dir_path)
    interpreter_dir_path = registry.get_interpreter_dir_path()
    venv_dir_path = interpreter_dir_path.joinpath('pip_venv')
    venv_context = _venv.create_venv(venv_dir_path)
    if venv_context:
        requirement_str = None
        if requirement.url:
            requirement_str = requirement.url
        else:
            requirement_str = str(requirement)
        _do_install(requirement_str, target_dir_path, venv_context)


# EOF
