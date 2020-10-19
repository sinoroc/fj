#

"""Pool."""

from __future__ import annotations

import importlib
import logging
import typing

import packaging

from . import base
from . import installers
from . import solve
from . import wheel

from . import _solver

if typing.TYPE_CHECKING:
    import pathlib

LOGGER = logging.getLogger(__name__)


class CanNotAddToPool(Exception):
    """Can not add to pool."""


def get_requirement_at_dir_path(
        requirement_dir_path: pathlib.Path,
) -> typing.Optional[base.Requirement]:
    """Get requirement corresponding to this directory."""
    #
    requirement = None
    #
    distribution = _solver.pool.find_distribution(requirement_dir_path)
    if distribution:
        requirement = _make_requirement_for_distribution(distribution)
    #
    return requirement


def _get_pooled_projects(
        registry: base.Registry,
) -> typing.List[base.Requirement]:
    #
    pooled_projects = []
    #
    pooled_distributions = _solver.pool.find_distributions(registry)
    for distribution in pooled_distributions:
        requirement = _make_requirement_for_distribution(distribution)
        pooled_projects.append(requirement)
    #
    return pooled_projects


def _make_requirement_for_distribution(
        distribution: importlib.metadata.Distribution,
) -> base.Requirement:
    #
    project_key = distribution.metadata['Name']
    version_str = distribution.metadata['Version']
    requirement_str = f'{project_key}=={version_str}'
    #
    requirement = packaging.requirements.Requirement(requirement_str)
    #
    return requirement


def _add_pooled_projects(
        registry: base.Registry,
        candidates: typing.Iterable[base.Candidate],
) -> None:
    #
    for candidate in candidates:
        _add_pooled_project(registry, candidate)


def _add_pooled_project(
        registry: base.Registry,
        candidate: base.Candidate,
) -> None:
    candidate_built_dist_path = getattr(candidate, 'path_built', None)
    if candidate_built_dist_path:
        project_key, release_version, tags = (
            wheel.parse_file_path(candidate_built_dist_path)
        )
        if project_key and release_version and tags:
            tags_str = _compress_tags(tags)
            pool_dir_path = registry.get_pool_dir_path()
            target_dir_str = f'{project_key}-{release_version}'
            target_dir_path = (
                pool_dir_path.joinpath(tags_str).joinpath(target_dir_str)
            )
            #
            installers.install_path(
                registry,
                candidate_built_dist_path,
                target_dir_path,
                False,  # editable
            )


def get_pooled_project_dir_path(
        registry: base.Registry,
        project_key: base.ProjectKey,
        version: base.Version,
) -> typing.Optional[pathlib.Path]:
    """Get path to directory containing installation of project release."""
    #
    dir_path = None
    #
    pooled_distributions = _solver.pool.find_distributions(registry)
    #
    for distribution in pooled_distributions:
        pooled_project_key = distribution.metadata['Name']
        if pooled_project_key == project_key:
            pooled_version_str = distribution.metadata['Version']
            if str(version) == pooled_version_str:
                maybe_dir_path = distribution.locate_file('')
                if maybe_dir_path:
                    dir_path = pathlib.Path(maybe_dir_path)
                #
                break
    #
    return dir_path


def _compress_tags(tags: base.Tags) -> str:
    #
    interpreters = set()
    abis = set()
    platforms = set()
    #
    for tag in tags:
        abis.add(tag.abi)
        interpreters.add(tag.interpreter)
        platforms.add(tag.platform)
    #
    tags_str = '-'.join(
        [
            '.'.join(sorted(interpreters)),
            '.'.join(sorted(abis)),
            '.'.join(sorted(platforms)),
        ]
    )
    #
    return tags_str


def add_candidates(
        registry: base.Registry,
        candidates: typing.Iterable[base.Candidate],
) -> None:
    """Add candidates to pool."""
    install_candidates = []
    for candidate in candidates:
        if not candidate.is_in_pool and hasattr(candidate, 'path_built'):
            install_candidates.append(candidate)
    if install_candidates:
        LOGGER.info("Adding to pool: %s", install_candidates)
        _add_pooled_projects(registry, install_candidates)
    else:
        LOGGER.info("Nothing to add to pool")


def add(
        registry: base.Registry,
        requirements: typing.Iterable[base.Requirement],
) -> None:
    """Add requirements to pool."""
    LOGGER.info("add_(%s)", requirements)
    resolution = solve.solve_for_pool(registry, requirements, False)
    if resolution:
        candidates = resolution.mapping.values()
        add_candidates(registry, candidates)
    else:
        LOGGER.info("Can not solve requirements!")


def list_(
        registry: base.Registry,
) -> typing.List[base.Requirement]:
    """List projects in the pool."""
    pooled_projects = _get_pooled_projects(registry)
    LOGGER.info("list_ %s", pooled_projects)
    return pooled_projects


# EOF
