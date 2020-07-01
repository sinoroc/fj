#

"""Command line interface."""

from __future__ import annotations

import argparse
import logging
import operator
import pathlib
import sys
import typing

from . import _config
from . import _context
from . import _meta

try:
    from . import _core
except ModuleNotFoundError:
    pass

if typing.TYPE_CHECKING:
    SubParsers = argparse._SubParsersAction  # pylint: disable=protected-access

LOGGER = logging.getLogger(__name__)


def output(line: str) -> None:
    """Output line of text (to console?)."""
    print(line)


def _add_cache_args_subparser(subparsers: SubParsers) -> None:
    cache_parser = subparsers.add_parser('cache', allow_abbrev=False)
    cache_parser.set_defaults(_handler=_cache_list)
    cache_subparsers = cache_parser.add_subparsers()
    #
    cache_list_parser = cache_subparsers.add_parser('list', allow_abbrev=False)
    cache_list_parser.set_defaults(_handler=_cache_list)


def _add_install_args_subparser(subparsers: SubParsers) -> None:
    install_parser = subparsers.add_parser('install', allow_abbrev=False)
    install_parser.set_defaults(_handler=_install)
    install_parser.add_argument(
        'requirements',
        metavar='requirement',
        nargs='+',
    )


def _add_links_args_subparser(subparsers: SubParsers) -> None:
    links_parser = subparsers.add_parser('links', allow_abbrev=False)
    links_parser.set_defaults(_handler=_links_list)
    links_subparsers = links_parser.add_subparsers()
    #
    links_list_parser = links_subparsers.add_parser('list', allow_abbrev=False)
    links_list_parser.set_defaults(_handler=_links_list)
    #
    link_parser = subparsers.add_parser('link', allow_abbrev=False)
    links_add_parser = links_subparsers.add_parser('add', allow_abbrev=False)
    for parser in [links_add_parser, link_parser]:
        parser.set_defaults(_handler=_links_add)
        parser.add_argument(
            'requirements',
            metavar='requirement',
            nargs='+',
        )
    #
    links_remove_parser = links_subparsers.add_parser(
        'remove',
        allow_abbrev=False,
    )
    unlink_parser = subparsers.add_parser('unlink', allow_abbrev=False)
    for parser in [links_remove_parser, unlink_parser]:
        parser.set_defaults(_handler=_links_remove)
        parser.add_argument(
            'requirements',
            metavar='project_name',
            nargs='+',
        )


def _add_pip_args_subparser(subparsers: SubParsers) -> None:
    pip_parser = subparsers.add_parser('pip', allow_abbrev=False)
    pip_subparsers = pip_parser.add_subparsers()
    #
    pip_install_parser = (
        pip_subparsers.add_parser('install', allow_abbrev=False)
    )
    pip_install_parser.set_defaults(_handler=_pip_install)
    pip_install_parser.add_argument(
        '--no-deps',
        action='store_true',
    )
    pip_install_parser.add_argument(
        '--exists-action',
    )
    pip_install_parser.add_argument(
        '-U',
        '--update',
        action='store_true',
    )
    pip_install_parser.add_argument(
        '-v',
        '--verbose',
        action='count',
    )
    #
    requirements_group = pip_install_parser.add_argument_group("Requirements")
    requirements_group.add_argument(
        '-e',
        '--editable',
        action='append',
        default=[],
        dest='editable_requirements',
        metavar='requirement',
    )
    requirements_group.add_argument(
        'requirements',
        metavar='requirement',
        nargs='*',
    )


def _add_pool_args_subparser(subparsers: SubParsers) -> None:
    pool_parser = subparsers.add_parser('pool', allow_abbrev=False)
    pool_parser.set_defaults(_handler=_pool_list)
    pool_subparsers = pool_parser.add_subparsers()
    #
    pool_add_parser = pool_subparsers.add_parser('add', allow_abbrev=False)
    pool_add_parser.set_defaults(_handler=_pool_add)
    pool_add_parser.add_argument(
        'requirements',
        metavar='requirement',
        nargs='+',
    )
    #
    pool_list_parser = pool_subparsers.add_parser('list', allow_abbrev=False)
    pool_list_parser.set_defaults(_handler=_pool_list)
    #
    pool_remove_parser = pool_subparsers.add_parser(
        'remove',
        allow_abbrev=False,
    )
    pool_remove_parser.set_defaults(_handler=_pool_remove)
    pool_remove_parser.add_argument(
        'requirements',
        metavar='requirement',
        nargs='+',
    )


def _add_ve_args_subparser(subparsers: SubParsers) -> None:
    ve_parser = subparsers.add_parser('ve', allow_abbrev=False)
    ve_parser.set_defaults(_handler=_ve)
    ve_parser.add_argument(
        'directory',
        default='.venv',
        nargs='?',
    )


def _build_args_parser(
        default_config_file_path: pathlib.Path,
) -> argparse.ArgumentParser:
    #
    parser = argparse.ArgumentParser(
        allow_abbrev=False,
        description=_meta.SUMMARY,
    )
    parser.add_argument(
        '--version',
        action='version',
        version=_meta.VERSION,
    )
    #
    parser.add_argument(
        '--configuration-file',
        default=str(default_config_file_path),
        type=argparse.FileType('r'),
        help=f"(default: {default_config_file_path})"
    )
    #
    parser.add_argument(
        '--python',
        default=sys.executable,
        type=argparse.FileType('r'),
    )
    #
    subparsers = parser.add_subparsers()
    #
    _add_cache_args_subparser(subparsers)
    _add_install_args_subparser(subparsers)
    _add_links_args_subparser(subparsers)
    _add_pip_args_subparser(subparsers)
    _add_pool_args_subparser(subparsers)
    _add_ve_args_subparser(subparsers)
    #
    solve_parser = subparsers.add_parser('solve', allow_abbrev=False)
    solve_parser.add_argument(
        'requirements',
        metavar='requirement',
        nargs='+',
    )
    solve_parser.set_defaults(_handler=_solve)
    #
    return parser


def _cache_list(_args: argparse.Namespace) -> None:
    cached_distributions = _core.cache_list()
    for cached_distribution in sorted(cached_distributions):
        output(str(cached_distribution))


def _install(args: argparse.Namespace) -> None:
    raw_requirement_strs = args.requirements
    _core.install(raw_requirement_strs, False)


def _links_add(args: argparse.Namespace) -> None:
    raw_requirement_strs = args.requirements
    _core.links_add(raw_requirement_strs)


def _links_list(_args: argparse.Namespace) -> None:
    linked_requirements = _core.links_list()
    sorted_linked_requirements = (
        sorted(linked_requirements, key=operator.attrgetter('name'))
    )
    for linked_requirement in sorted_linked_requirements:
        output(str(linked_requirement))


def _links_remove(args: argparse.Namespace) -> None:
    raw_requirement_strs = args.requirements
    _core.links_remove(raw_requirement_strs)


def _pip_install(args: argparse.Namespace) -> None:
    _core.pip_install(
        args.requirements,
        args.editable_requirements,
        args.no_deps,
    )


def _pool_add(args: argparse.Namespace) -> None:
    raw_requirement_strs = args.requirements
    _core.pool_add(raw_requirement_strs)


def _pool_list(_args: argparse.Namespace) -> None:
    available_projects = _core.pool_list()
    sorted_available_projects = (
        sorted(available_projects, key=operator.attrgetter('name'))
    )
    for available_project in sorted_available_projects:
        output(str(available_project))


def _pool_remove(args: argparse.Namespace) -> None:
    raw_requirement_strs = args.requirements
    _core.pool_remove(raw_requirement_strs)


def _solve(args: argparse.Namespace) -> None:
    raw_requirement_strs = args.requirements
    _core.solve(raw_requirement_strs)


def _ve(args: argparse.Namespace) -> None:
    venv_dir_str = args.directory
    _core.ve_create(venv_dir_str)


def main() -> None:
    """CLI main function."""
    #
    logging.basicConfig(level=logging.INFO)
    LOGGER.info("Current interpreter: %s", sys.executable)
    #
    project_name = _meta.PROJECT_NAME
    #
    default_config_file_path = (
        _config.get_default_config_file_path(project_name)
    )
    #
    args_parser = _build_args_parser(default_config_file_path)
    args = args_parser.parse_args()
    LOGGER.info("Arguments: %s", vars(args))
    #
    if hasattr(args, '_handler'):
        if _context.is_switch_needed(args):
            LOGGER.info("Command needs to be executed in a different context.")
            _context.switch(project_name, args)
        else:
            args._handler(args)  # pylint: disable=protected-access
    else:
        args_parser.print_usage()


# EOF
