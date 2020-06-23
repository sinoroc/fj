#

"""Tox plugin."""

from __future__ import annotations

import typing

import tox

if typing.TYPE_CHECKING:
    import argparse


@tox.hookimpl  # type: ignore[misc]
def tox_addoption(parser: tox.config.Parser) -> None:
    """Set hook."""
    #
    parser.argparser.add_argument(
        '--fj',
        action='store_true',
    )


@tox.hookimpl  # type: ignore[misc]
def tox_configure(config: tox.config.Config) -> None:
    """Set hook."""
    #
    is_fj_installer_enabled = (config.option.fj is True)
    #
    if is_fj_installer_enabled:
        #
        default_install_command_str = tox.config.InstallcmdOption.default
        default_install_command = default_install_command_str.split()
        #
        for envconfig in config.envconfigs.values():
            #
            if envconfig.install_command == default_install_command:
                #
                envconfig.install_command = [
                    'python',
                    '-m',
                    'fj',
                    'pip',
                    'install',
                    '{opts}',
                    '{packages}',
                ]


# EOF
