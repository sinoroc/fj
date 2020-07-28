#

"""Handle subprocesses."""

from __future__ import annotations

import logging
import typing
import subprocess

LOGGER = logging.getLogger(__name__)


def call(command: typing.List[str]) -> None:
    """Call subprocess."""
    LOGGER.info("Subprocess command: %s", command)
    subprocess.check_call(command)


# EOF
