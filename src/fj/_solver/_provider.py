#

"""Provider for the dependency solver."""

from __future__ import annotations

import operator
import typing

import packaging.utils
import resolvelib

if typing.TYPE_CHECKING:
    from . import base


class Provider(resolvelib.providers.AbstractProvider):  # type: ignore[misc]
    """Provider for 'resolvelib'."""

    def __init__(
            self,
            registry: base.Registry,
            candidates_finders: typing.Iterable[base.CandidateFinder],
            skip_dependencies: bool,
    ):
        """Initialize."""
        self._candidates_finders = candidates_finders
        self._registry = registry
        self._skip_dependencies = skip_dependencies

    def identify(
            self,
            dependency: base.Requirement,
    ) -> base.ProjectKey:
        """Implement abstract."""
        project_key = packaging.utils.canonicalize_name(dependency.name)
        return project_key

    def find_matches(
            self,
            requirements: typing.Sequence[base.Requirement],
    ) -> typing.List[base.Candidate]:
        """Implement abstract.

        Make sure that candidates are still sorted in order of priority, for
        example candidates that are already active should have priority over
        candidates from the pool, and those should have priority over those
        from a remote index.
        If it can be assumed that the finders are already sorted by order of
        priority, then that job is easy.
        """
        #
        matches = []
        #
        # All requirements are guaranteed to have the same key but might have
        # different specifiers.
        project_key = packaging.utils.canonicalize_name(requirements[0].name)
        #
        extras = set()
        for requirement in requirements:
            extras.update(requirement.extras)
        #
        for candidates_finder in self._candidates_finders:
            unsorted_candidates = candidates_finder.find_candidates(
                project_key,
                requirements,
                extras,
            )
            if unsorted_candidates:
                candidates = sorted(
                    unsorted_candidates,
                    key=operator.attrgetter('release_version'),
                    reverse=True,
                )
                direct_candidate = None
                for candidate in candidates:
                    if candidate.is_direct:
                        direct_candidate = candidate
                        break
                if not direct_candidate:
                    matches.extend(candidates)
                else:
                    matches = [direct_candidate]
                    break
        #
        return matches

    def get_preference(
            self,
            resolution: typing.Optional[base.Candidate],
            candidates: typing.Sized,
            information: typing.Any,
    ) -> int:
        """Implement abstract."""
        preference = len(candidates)
        return preference

    def get_dependencies(
            self,
            candidate: base.Candidate,
    ) -> typing.List[base.Requirement]:
        """Implement abstract."""
        #
        dependencies = []
        if not self._skip_dependencies:
            dependencies = candidate.dependencies
        #
        return dependencies

    def is_satisfied_by(
            self,
            requirement: base.Requirement,
            candidate: base.Candidate,
    ) -> bool:
        """Implement abstract."""
        #
        # Aren't matched candidates already supposed to have been checked and
        # filtered? Is that redundant? Should we always return true?
        #
        project_key = packaging.utils.canonicalize_name(requirement.name)
        is_satisfied = (
            candidate.project_key == project_key
            and candidate.release_version in requirement.specifier
        )
        return is_satisfied


# EOF
