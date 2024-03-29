#

"""Handle links."""

from __future__ import annotations

import logging
import pathlib
import typing

import packaging

from . import base
from . import pool
from . import solve

LOGGER = logging.getLogger(__name__)

PATH_CONFIG_FILE_NAME = 'fj-links.pth'


class CanNotLinkDirectCandidate(Exception):
    """Can not link candidate for a requirement with a direct URI."""


def _get_path_config_file_path(
        registry: base.Registry,
) -> pathlib.Path:
    #
    path_config_file_path = (
        registry.environment.purelib_dir_path.joinpath(PATH_CONFIG_FILE_NAME)
    )
    return path_config_file_path


def _read_linked_requirements(
        registry: base.Registry,
) -> typing.List[base.Requirement]:
    #
    linked_requirements = []
    #
    path_config_file_path = _get_path_config_file_path(registry)
    #
    if path_config_file_path.exists() and path_config_file_path.is_file():
        with path_config_file_path.open('rt') as path_config_file:
            for line in path_config_file.readlines():
                link_path = pathlib.Path(line.strip())
                linked_requirement = (
                    pool.get_requirement_at_dir_path(link_path)
                )
                if linked_requirement:
                    linked_requirements.append(linked_requirement)
    #
    return linked_requirements


def _write_links(
        registry: base.Registry,
        requirements: typing.Sequence[base.Requirement],
) -> None:
    #
    path_config_file_path = _get_path_config_file_path(registry)
    #
    link_strs = []
    for requirement in requirements:
        req_version_str = base.get_pinned_requirement_version_str(requirement)
        if req_version_str:
            req_version = packaging.version.Version(req_version_str)
            requirement_key = (
                packaging.utils.canonicalize_name(requirement.name)
            )
            dir_path = pool.get_pooled_project_dir_path(
                registry,
                requirement_key,
                req_version,
            )
            link_strs.append(str(dir_path))
    #
    links_str = '\n'.join(link_strs)
    #
    LOGGER.info("_write_links(%s) to %s", requirements, path_config_file_path)
    path_config_file_path.write_text(links_str)


def list_(
        registry: base.Registry,
) -> typing.List[base.Requirement]:
    """List links."""
    linked_requirements = _read_linked_requirements(registry)
    return linked_requirements


def _add(
        linked_requirements: typing.MutableSequence[base.Requirement],
        requirement: base.Requirement,
) -> None:
    already_linked = False
    requirement_key = packaging.utils.canonicalize_name(requirement.name)
    for linked_requirement in linked_requirements:
        linked_requirement_key = (
            packaging.utils.canonicalize_name(linked_requirement.name)
        )
        if linked_requirement_key == requirement_key:
            already_linked = True
            break
    if not already_linked:
        linked_requirements.append(requirement)


def _add_linked_requirements(
        registry: base.Registry,
        requirements: typing.Sequence[base.Requirement],
) -> None:
    linked_requirements = _read_linked_requirements(registry)
    for requirement in requirements:
        _add(linked_requirements, requirement)
    _write_links(registry, linked_requirements)


def add_candidates(
        registry: base.Registry,
        candidates: typing.Iterable[base.Candidate],
) -> None:
    """Add candidates as links."""
    requirements = []
    for candidate in candidates:
        requirement_str = (
            f'{candidate.project_key}=={candidate.release_version}'
        )
        requirement = packaging.requirements.Requirement(requirement_str)
        requirements.append(requirement)
    #
    if requirements:
        LOGGER.info("Adding to links: %s", requirements)
        _add_linked_requirements(registry, requirements)
    else:
        LOGGER.info("Nothing to link")


def add(
        registry: base.Registry,
        requirements: typing.Sequence[base.Requirement],
) -> None:
    """Add links to requirements."""
    LOGGER.info("add %s", requirements)
    resolution = solve.solve_for_environment(
        registry,
        requirements,
        False,
    )
    if resolution:
        candidates = []
        for candidate in resolution.mapping.values():
            if not candidate.is_direct:
                if not candidate.is_in_environment and candidate.is_in_pool:
                    candidates.append(candidate)
            else:
                raise CanNotLinkDirectCandidate(candidate)
        #
        if candidates:
            add_candidates(registry, candidates)
    else:
        LOGGER.info("Can not solve requirements!")


def _remove(
        requirements: typing.List[base.Requirement],
        requirement: base.Requirement,
) -> None:
    requirement_key = packaging.utils.canonicalize_name(requirement.name)
    for linked_requirement in requirements:
        linked_requirement_key = (
            packaging.utils.canonicalize_name(linked_requirement.name)
        )
        if linked_requirement_key == requirement_key:
            requirements.remove(linked_requirement)
            break


def remove(
        registry: base.Registry,
        requirements: typing.List[base.Requirement],
) -> None:
    """Remove links to requirements."""
    LOGGER.info("remove %s", requirements)
    linked_requirements = _read_linked_requirements(registry)
    for requirement in requirements:
        _remove(linked_requirements, requirement)
    _write_links(registry, linked_requirements)
    LOGGER.info("remove()->%s", linked_requirements)


# EOF
