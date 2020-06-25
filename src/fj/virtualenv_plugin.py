#

"""Virtualenv plugin."""

from __future__ import annotations

import logging
import typing

import packaging.tags
import packaging.version
import virtualenv.seed.embed.base_embed

from . import _config
from . import _install
from . import _meta
from . import _solver
from . import _subprocess
from . import _zipapp

if typing.TYPE_CHECKING:
    import argparse
    import pathlib

LOGGER = logging.getLogger(__name__)


class UnknownPythonBitness(Exception):
    """Unknown Python bitness."""


class UnknownPythonPlatform(Exception):
    """Unknown Python platform."""


def _get_interpreter_str(
        python_implementation_str: str,
        python_version: packaging.version.Version,
) -> str:
    long_name = python_implementation_str.lower()
    short_name = packaging.tags.INTERPRETER_SHORT_NAMES[long_name]
    interpreter_str = (
        f'{short_name}'
        f'{python_version.major}'
        f'{python_version.minor}'
    )
    return interpreter_str


def _get_python_processor_str(
        creator: virtualenv.create.creator.Creator,
) -> str:
    #
    python_processor_str = None
    platform_name = creator.interpreter.platform
    if platform_name == 'linux':
        bitness = creator.interpreter.architecture
        if bitness == 64:
            python_processor_str = 'x86_64'
        else:
            raise UnknownPythonBitness(bitness)
    else:
        raise UnknownPythonPlatform(platform_name)
    return python_processor_str


def _get_python_version(
        creator: virtualenv.create.creator.Creator,
) -> packaging.version.Version:
    #
    python_version_list = [
        str(creator.interpreter.version_info.major),
        str(creator.interpreter.version_info.minor),
        str(creator.interpreter.version_info.micro),
    ]
    python_version_str = '.'.join(python_version_list)
    python_version = packaging.version.Version(python_version_str)
    return python_version


def _get_platforms(
        python_processor_str: str,
        creator: virtualenv.create.creator.Creator,
) -> typing.List[str]:
    #
    platform_name = creator.interpreter.platform
    if platform_name == 'linux':
        platform = f'{creator.interpreter.platform}_{python_processor_str}'
    else:
        raise UnknownPythonPlatform(platform_name)
    platforms = [platform]
    return platforms


def _get_tags(
        python_processor_str: str,
        python_implementation_str: str,
        python_version: packaging.version.Version,
        creator: virtualenv.create.creator.Creator,
) -> _solver.base.Tags:
    """Get the tags.

    This is a best effort guess, hopefully it's good enough for the seeds.
    """
    #
    python_version_set = [python_version.major, python_version.minor]
    #
    interpreter_str = _get_interpreter_str(
        python_implementation_str,
        python_version,
    )
    #
    platforms = _get_platforms(python_processor_str, creator)
    #
    tag_list = []
    #
    if python_implementation_str == 'CPython':
        cpython_tags = list(
            packaging.tags.cpython_tags(
                python_version=python_version_set,
                platforms=platforms,
            ),
        )
        tag_list.extend(cpython_tags)
    else:
        generic_tags = list(
            packaging.tags.generic_tags(
                interpreter=interpreter_str,
                platforms=platforms,
            ),
        )
        tag_list.extend(generic_tags)
    #
    compatible_tags = list(
        packaging.tags.compatible_tags(
            python_version=python_version_set,
            interpreter=interpreter_str,
            platforms=platforms,
        ),
    )
    tag_list.extend(compatible_tags)
    #
    tags: _solver.base.Tags = frozenset(tag_list)
    #
    return tags


def _get_purelib_dir_path(
        creator: virtualenv.create.creator.Creator,
) -> pathlib.Path:
    # It is counter intuitive but it should indeed deliver the path to
    # the 'purelib' directory for the newly created environment, and
    # not the one of the 'creator'.
    purelib_dir_path: pathlib.Path = creator.purelib
    return purelib_dir_path


def _make_environment(
        creator: virtualenv.create.creator.Creator,
) -> _solver.base.Environment:
    #
    purelib_dir_path = _get_purelib_dir_path(creator)
    #
    python_implementation_str = creator.interpreter.implementation
    #
    python_processor_str = _get_python_processor_str(creator)
    #
    python_version = _get_python_version(creator)
    #
    # Probably safe to assume there is nothing in the virtual environment yet
    # and since 'search_path' is only used to find active candidates (i.e.
    # installed or linked distributions) setting an empty search path
    # should be good enough. (Maybe not if 'site-packages' are supposed to
    # be enabled.)
    search_path: typing.List[str] = []
    #
    tags = _get_tags(
        python_processor_str,
        python_implementation_str,
        python_version,
        creator,
    )
    #
    environment = _solver.base.Environment(
        purelib_dir_path,
        python_implementation_str,
        python_processor_str,
        python_version,
        search_path,
        tags,
    )
    #
    return environment


class FjVirtualenvSeeder(
        virtualenv.seed.embed.base_embed.BaseEmbed,  # type: ignore[misc]
):
    """Virtualenv seed plugin."""

    def __init__(
            self,
            options: virtualenv.config.cli.parser.VirtualEnvOptions,
    ) -> None:
        """Initialize."""
        super().__init__(options)
        #
        self._requirement_str = options.fj_requirement

    def run(self, creator: virtualenv.create.creator.Creator) -> None:
        """Implement abstract."""
        #
        if self.enabled:
            #
            project_name = _meta.PROJECT_NAME
            #
            environment = _make_environment(creator)
            #
            requirement_strs = [
                self._requirement_str,
                'pip',
                'setuptools',
                'wheel',
            ]
            #
            if self._is_context_switch_needed(environment):
                _run_in_context(creator, project_name, requirement_strs)
            else:
                _run(environment, project_name, requirement_strs)

    def _is_context_switch_needed(
            self,
            environment: _solver.base.Environment,
    ) -> bool:
        _dummy = (self, environment)
        return False

    @classmethod
    def add_parser_arguments(
            cls,
            parser: argparse._ArgumentGroup,  # pylint:disable=protected-access
            interpreter: virtualenv.discovery.py_info.PythonInfo,
            app_data: virtualenv.app_data.base.AppData,
    ) -> None:
        """Override."""
        super().add_parser_arguments(parser, interpreter, app_data)
        parser.add_argument(
            f'--{_meta.PROJECT_NAME}-requirement',
            default=f'{_meta.PROJECT_NAME}',
        )


def _run(
        environment: _solver.base.Environment,
        project_name: str,
        requirement_strs: typing.Iterable[str],
) -> None:
    build_registry = _solver.base.build_registry
    with build_registry(project_name, environment) as registry:
        requirements = _solver.parser.parse(registry, requirement_strs)
        _install.install(registry, requirements, [], False)


def _run_in_context(
        creator: virtualenv.create.creator.Creator,
        project_name: str,
        requirement_strs: typing.List[str],
) -> None:
    #
    config_file_path = (
        _config.get_default_config_file_path(project_name)
    )
    #
    with config_file_path.open() as config_file:
        config = _config.parse_config(project_name, config_file)
    #
    zipapp_path = _zipapp.get_or_build_zipapp_path(config)
    #
    command = [
        str(creator.exe),
        str(zipapp_path),
        'install',
    ] + requirement_strs
    #
    _subprocess.call(command)


# EOF
