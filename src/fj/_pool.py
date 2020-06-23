#

"""Pool."""

from __future__ import annotations

import logging
import shutil
import typing

import packaging

from . import _pip
from . import _solver

LOGGER = logging.getLogger(__name__)


class CanNotAddToPool(Exception):
    """Can not add to pool."""


def _get_pooled_projects(
        registry: _solver.base.Registry,
) -> typing.List[_solver.base.Requirement]:
    #
    pooled_projects = []
    pool_dir_path = registry.get_pool_dir_path()
    if pool_dir_path.is_dir():
        for item_path in pool_dir_path.iterdir():
            if item_path.is_dir():
                absolute_path = item_path.resolve()
                requirement = registry.get_requirement_for_dir_path(
                    absolute_path,
                )
                if requirement:
                    pooled_projects.append(requirement)
    #
    return pooled_projects


def _add_pooled_projects(
        registry: _solver.base.Registry,
        requirements: typing.Iterable[_solver.base.Requirement],
) -> None:
    for requirement in requirements:
        target_dir_path = (
            registry.get_requirement_dir_path(requirement)
        )
        if target_dir_path:
            _pip.install_requirement(registry, requirement, target_dir_path)
        else:
            raise CanNotAddToPool(requirement)


def add_candidates(
        registry: _solver.base.Registry,
        candidates: typing.Iterable[_solver.base.Candidate],
) -> None:
    """Add candidates to pool."""
    requirements = []
    for candidate in candidates:
        if not candidate.is_in_pool:
            requirement_str = (
                f'{candidate.project_key}=={candidate.release_version}'
            )
            requirement = packaging.requirements.Requirement(requirement_str)
            if candidate.is_direct and hasattr(candidate, 'path'):
                requirement.url = getattr(candidate, 'path', None)
            requirements.append(requirement)
    if requirements:
        LOGGER.info("Adding to pool: %s", requirements)
        _add_pooled_projects(registry, requirements)
    else:
        LOGGER.info("Nothing to add to pool")


def add(
        registry: _solver.base.Registry,
        requirements: typing.Iterable[_solver.base.Requirement],
) -> None:
    """Add requirements to pool."""
    LOGGER.info("add_(%s)", requirements)
    resolution = _solver.solve.solve_for_pool(registry, requirements, False)
    if resolution:
        candidates = resolution.mapping.values()
        add_candidates(registry, candidates)
    else:
        LOGGER.info("Can not solve requirements!")


def list_(
        registry: _solver.base.Registry,
) -> typing.List[_solver.base.Requirement]:
    """List projects in the pool."""
    pooled_projects = _get_pooled_projects(registry)
    LOGGER.info("list_ %s", pooled_projects)
    return pooled_projects


def remove(
        registry: _solver.base.Registry,
        requirements: typing.Iterable[_solver.base.Requirement],
) -> None:
    """Remove requirements from pool."""
    for requirement in requirements:
        target_dir_path = registry.get_requirement_dir_path(requirement)
        if target_dir_path and target_dir_path.is_dir():
            shutil.rmtree(target_dir_path)


# EOF
