#

"""Consider active distributions as candidates."""

from __future__ import annotations

import logging
import sys
import typing

import importlib.metadata

from . import base

LOGGER = logging.getLogger(__name__)


class _ActiveCandidate(base.BaseCandidate):
    """Active distribution as a candidate for dependency resolution."""

    def __init__(
            self,
            distribution: importlib.metadata.Distribution,
            extras: base.Extras,
    ) -> None:
        """Initialize."""
        super().__init__(extras)
        #
        self._distribution = distribution

    @property
    def is_in_environment(self) -> bool:
        """Implement abstract."""
        return True

    def _get_metadata(self) -> base.Metadata:
        """Implement abstract."""
        return self._distribution.metadata  # type: ignore[return-value]


def _get_search_path(registry: base.Registry) -> typing.List[str]:
    """Get search path.

    In case we are running from a 'zipapp', the file itself is added to the top
    of the search path, so we want to exclude it from our search.
    """
    env_search_path = registry.environment.search_path
    if sys.argv and env_search_path and sys.argv[0] == env_search_path[0]:
        search_path = env_search_path[1:]
    else:
        search_path = env_search_path
    return search_path


class ActiveFinder(
        base.CandidateFinder,
):  # pylint: disable=too-few-public-methods
    """Find candidates among the active distributions."""

    def __init__(
            self,
            registry: base.Registry,
    ) -> None:
        """Initialize."""
        #
        self._registry = registry
        #
        self._search_context = importlib.metadata.DistributionFinder.Context(
            path=_get_search_path(self._registry),
        )

    def find_candidates(
            self,
            project_key: base.ProjectKey,
            requirements: typing.Iterable[base.Requirement],
            extras: base.Extras,
    ) -> typing.Iterator[base.Candidate]:
        """Implement abstract."""
        #
        distributions_iterator = importlib.metadata.distributions(
            context=self._search_context,
        )
        for distribution in distributions_iterator:
            candidate = _ActiveCandidate(distribution, extras)
            is_compatible = candidate.is_compatible(
                requirements,
                self._registry.environment,
            )
            if is_compatible:
                yield candidate
                # Shouldn't there always be only 1 active distribution per key?


# EOF
