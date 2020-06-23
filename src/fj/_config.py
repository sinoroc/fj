#

"""Configuration."""

from __future__ import annotations

import configparser
import os
import pathlib
import platform
import typing

if typing.TYPE_CHECKING:
    Config = typing.Dict[str, typing.Any]


def parse_config(project_name: str, config_file: typing.TextIO) -> Config:
    """Parse config file."""
    #
    raw_config = configparser.ConfigParser()
    raw_config.read_file(config_file)
    #
    main_section_name = f'{project_name}:main'
    #
    requirements = [
        line.strip()
        for line in raw_config[main_section_name]['requirements'].splitlines()
        if line.strip()
    ]
    #
    config = {
        'main': {
            'project_name': project_name,
        },
        'zipapp': {
            'requirements': requirements,
        },
    }
    #
    return config


def _get_windows_user_app_data_dir_path() -> pathlib.Path:
    #
    user_app_data_dir_path = None
    #
    if 'APPDATA' in os.environ:
        user_app_data_dir_path = pathlib.Path(os.environ['APPDATA'])
    else:
        user_app_data_dir_path = (
            pathlib.Path.home().joinpath('AppData', 'Roaming')
        )
    #
    return user_app_data_dir_path


def _get_user_config_dir_path(project_name: str) -> pathlib.Path:
    """Get path to user's configuration directory for the application."""
    #
    system = platform.system()
    if system == 'Windows':
        windows_user_app_data_dir_path = _get_windows_user_app_data_dir_path()
        app_user_config_dir_path = (
            windows_user_app_data_dir_path.joinpath('config')
        )
    elif system == 'Linux':
        user_config_dir_path = None
        if 'XDG_CONFIG_HOME' in os.environ:
            user_config_dir_path = pathlib.Path(os.environ['XDG_CONFIG_HOME'])
        else:
            user_config_dir_path = pathlib.Path.home().joinpath('.config')
        #
        if user_config_dir_path:
            app_user_config_dir_path = (
                user_config_dir_path.joinpath(project_name)
            )
    #
    return app_user_config_dir_path


def get_user_data_dir_path(project_name: str) -> pathlib.Path:
    """Get path to directory for user data."""
    #
    system = platform.system()
    if system == 'Windows':
        windows_user_app_data_dir_path = _get_windows_user_app_data_dir_path()
        app_user_data_dir_path = (
            windows_user_app_data_dir_path.joinpath('data')
        )
    elif system == 'Linux':
        user_data_dir_path = None
        if 'XDG_DATA_HOME' in os.environ:
            user_data_dir_path = pathlib.Path(os.environ['XDG_DATA_HOME'])
        else:
            user_data_dir_path = (
                pathlib.Path.home().joinpath('.local', 'share')
            )
        #
        if user_data_dir_path:
            app_user_data_dir_path = (
                user_data_dir_path.joinpath(project_name)
            )
    #
    return app_user_data_dir_path


def get_default_config_file_path(project_name: str) -> pathlib.Path:
    """Get default path to configuration file."""
    #
    config_file_name = f'{project_name}.cfg'
    config_dir_path = _get_user_config_dir_path(project_name)
    config_file_path = config_dir_path.joinpath(config_file_name)
    #
    return config_file_path


# EOF
