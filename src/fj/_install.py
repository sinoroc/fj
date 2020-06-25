#

"""Install."""

from __future__ import annotations

import logging
import typing

import packaging

from . import _links
from . import _pip
from . import _pool
from . import _solver

LOGGER = logging.getLogger(__name__)


class CanNotInstallWithoutPath(Exception):
    """Can not install candidate without path."""


def _install_candidates(  # pylint: disable=too-complex
        registry: _solver.base.Registry,
        candidates: typing.Iterable[_solver.base.Candidate],
        editable_candidates: typing.Iterable[_solver.base.Candidate],
) -> None:
    #
    candidates_to_install = []
    candidates_to_link = []
    candidates_to_pool = []
    #
    for candidate in candidates:
        if candidate.is_direct:
            candidates_to_install.append(candidate)
        elif not candidate.is_in_environment:
            candidates_to_link.append(candidate)
            if not candidate.is_in_pool:
                candidates_to_pool.append(candidate)
    #
    if candidates_to_pool:
        _pool.add_candidates(registry, candidates_to_pool)
    #
    if candidates_to_link:
        _links.add_candidates(registry, candidates_to_link)
    #
    for candidate in candidates_to_install:
        candidate_path = getattr(candidate, 'path', None)
        if candidate_path:
            _pip.install_path(registry, candidate_path)
        else:
            CanNotInstallWithoutPath(candidate)
    #
    for candidate in editable_candidates:
        candidate_path = getattr(candidate, 'source_path', None)
        if candidate_path:
            _pip.install_path(registry, candidate_path, editable=True)
        else:
            CanNotInstallWithoutPath(candidate)


class CanNotInstallIndirectRequirementAsEditable(Exception):
    """Can not install indirect requirement as editable."""


def install(
        registry: _solver.base.Registry,
        requirements: typing.Iterable[_solver.base.Requirement],
        editable_requirements: typing.Iterable[_solver.base.Requirement],
        skip_dependencies: bool,
) -> None:
    """Install requirements."""
    #
    editable_keys = []
    for requirement in editable_requirements:
        project_key = packaging.utils.canonicalize_name(requirement.name)
        editable_keys.append(project_key)
        if not requirement.url:
            raise CanNotInstallIndirectRequirementAsEditable(requirement)
    #
    all_requirements = list(requirements) + list(editable_requirements)
    #
    resolution = _solver.solve.solve_for_environment(
        registry,
        all_requirements,
        skip_dependencies,
    )
    #
    if resolution is None:
        resolution = _solver.solve.solve(
            registry,
            all_requirements,
            skip_dependencies,
        )
    #
    if resolution:
        candidates = []
        editable_candidates = []
        #
        all_candidates = resolution.mapping.values()
        for candidate in all_candidates:
            if candidate.project_key in editable_keys:
                editable_candidates.append(candidate)
            else:
                candidates.append(candidate)
        _install_candidates(registry, candidates, editable_candidates)


# EOF
