#

"""Candidates for direct URI requirements."""

from __future__ import annotations

import typing

import packaging

from . import base


class MultipleDirectUriRequirements(Exception):
    """Can not solve multiple direct requirements for the same project key."""


class DirectCandidateFinder(  # pylint: disable=too-few-public-methods
        base.CandidateFinder,
):
    """Find candidates for requirements with direct URI."""

    def __init__(
            self,
            registry: base.Registry,
            requirements: typing.Iterable[base.Requirement],
            candidate_makers: typing.Iterable[base.CandidateMaker],
    ) -> None:
        """Initialize."""
        #
        super().__init__()
        #
        self._registry = registry
        self._candidate_makers = candidate_makers
        #
        self._direct_requirements = _find_direct_requirements(requirements)

    def find_candidates(
            self,
            project_key: base.ProjectKey,
            requirements: typing.Iterable[base.Requirement],
            extras: base.Extras,
    ) -> typing.Iterator[base.Candidate]:
        """Implement abstract."""
        #
        candidate = None
        #
        if project_key in self._direct_requirements:
            direct_requirement = self._direct_requirements[project_key]
            for candidate_maker in self._candidate_makers:
                candidate = candidate_maker.make_from_direct_requirement(
                    self._registry,
                    direct_requirement,
                    extras,
                )
                if candidate:
                    break  # There should be only 1 candidate per project key.
        #
        if candidate:
            yield candidate


def _find_direct_requirements(
        requirements: typing.Iterable[base.Requirement],
) -> typing.Mapping[base.ProjectKey, base.Requirement]:
    #
    # If there is more than 1 direct requirement for the same project key
    # then it is a user error, and an exception should be raised.
    #
    direct_requirements = {}
    #
    for requirement in requirements:
        if requirement.url:
            project_key = packaging.utils.canonicalize_name(requirement.name)
            if project_key not in direct_requirements:
                direct_requirements[project_key] = requirement
            else:
                raise MultipleDirectUriRequirements(requirements)
    #
    return direct_requirements


# EOF
