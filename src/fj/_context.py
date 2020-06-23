#

"""Handle context switch."""

from __future__ import annotations

import logging
import pathlib
import sys
import typing

from . import _config
from . import _subprocess
from . import _zipapp

try:
    from . import _core  # pylint: disable=unused-import
except ImportError:
    DEPENDENCIES_MISSING = True
else:
    DEPENDENCIES_MISSING = False

if typing.TYPE_CHECKING:
    import argparse

LOGGER = logging.getLogger(__name__)


def is_switch_needed(args: argparse.Namespace) -> bool:
    """Check if a context switch is needed."""
    #
    is_needed = True
    #
    python_interpreter_path_str = (
        str(pathlib.Path.cwd().joinpath(args.python.name))
    )
    if python_interpreter_path_str == sys.executable:
        if not DEPENDENCIES_MISSING:
            is_needed = False
        else:
            LOGGER.info("Needs context switch since dependencies are missing.")
    else:
        LOGGER.info(
            (
                "Needs context switch since the current Python interpreter "
                "(%s) is not the same as the target (%s)."
            ),
            sys.executable,
            python_interpreter_path_str,
        )
    #
    return is_needed


def switch(project_name: str, args: argparse.Namespace) -> None:
    """Switch context."""
    #
    config = _config.parse_config(project_name, args.configuration_file)
    LOGGER.info("Configuration: %s", config)
    zipapp_path = _zipapp.get_or_build_zipapp_path(config)
    LOGGER.info("Zipapp: %s", zipapp_path)
    #
    command = [
        args.python.name,
        str(zipapp_path),
        *sys.argv[1:],
    ]
    #
    LOGGER.info("Context switch...")
    _subprocess.call(command)
    LOGGER.info("Context switch done.")


# EOF
