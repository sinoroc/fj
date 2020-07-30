#

"""Wrapper for pip."""

from __future__ import annotations

import logging
import sys
import typing

from . import subprocess_wrapper
from . import venv_wrapper

if typing.TYPE_CHECKING:
    import pathlib

LOGGER = logging.getLogger(__name__)


def install(
        requirement_str: str,
        target_dir_path: typing.Optional[pathlib.Path] = None,
        venv_context: typing.Optional[venv_wrapper.VenvContext] = None,
        editable: bool = False,
) -> None:
    """Install with 'pip' in a subprocess.

    Use either the current Python interpreter or the one in the 'venv' context.
    """
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
    LOGGER.info("install %s", command)
    subprocess_wrapper.call(command)


def wheel(
        source_dir_path: pathlib.Path,
        target_dir_path: pathlib.Path,
) -> None:
    """Build a wheel with 'pip' in a subprocess."""
    command = [
        sys.executable,
        '-m',
        'pip',
        'wheel',
        '--no-deps',
        '--wheel-dir',
        str(target_dir_path),
        str(source_dir_path),
    ]
    LOGGER.info("wheel %s", command)
    subprocess_wrapper.call(command)


# EOF
