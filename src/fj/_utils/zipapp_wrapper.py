#

"""Zipapp."""

from __future__ import annotations

import logging
import pathlib
import tempfile
import typing
import zipapp

from . import config
from . import venv_wrapper
from . import subprocess_wrapper

LOGGER = logging.getLogger(__name__)


def get_or_build_zipapp_path(configuration: config.Config) -> pathlib.Path:
    """Get or build zipapp."""
    #
    zipapp_path = _get_zipapp_path(configuration)
    #
    if not zipapp_path.is_file():
        LOGGER.info("Building zipapp...")
        _build_zipapp(configuration, zipapp_path)
    #
    return zipapp_path


def _get_zipapp_path(configuration: config.Config) -> pathlib.Path:
    project_name = configuration['main']['project_name']
    user_data_dir_path = config.get_user_data_dir_path(project_name)
    zipapp_path = user_data_dir_path.joinpath('zipapp', f'{project_name}.pyz')
    return zipapp_path


def _build_zipapp(
        configuration: config.Config,
        zipapp_path: pathlib.Path,
) -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = pathlib.Path(temp_dir)
        #
        venv_dir_path = temp_dir_path.joinpath('venv')
        LOGGER.info("Creating virtual environment to build zipapp...")
        venv_context = venv_wrapper.create_venv(venv_dir_path)
        if venv_context:
            LOGGER.info("Virtual environment creation done.")
            #
            requirement_str_list = configuration['zipapp']['requirements']
            #
            install_dir_path = temp_dir_path.joinpath('zipapp')
            LOGGER.info("Installing zipapp requirements...")
            python_exe = venv_context.env_exe
            _do_pip_install(
                pathlib.Path(python_exe),
                install_dir_path,
                requirement_str_list,
            )
            #
            zipapp_dir_path = zipapp_path.parent
            if not zipapp_dir_path.is_dir():
                zipapp_dir_path.mkdir(parents=True)
            #
            zipapp.create_archive(
                install_dir_path,
                interpreter='/usr/bin/env python3',
                main='fj._cli.main:main',
                target=zipapp_path,
            )


def _do_pip_install(
        python_exe_path: pathlib.Path,
        target_dir_path: pathlib.Path,
        requirement_str_list: typing.Iterable[str],
) -> None:
    #
    command = [
        str(python_exe_path),
        '-m',
        'pip',
        'install',
        '--target',
        str(target_dir_path),
        *requirement_str_list,
    ]
    #
    LOGGER.info("Calling pip subprocess...")
    subprocess_wrapper.call(command)
    LOGGER.info("Calling pip subprocess done.")


# EOF
