#

"""Find candidates on a PEP503 index."""

from __future__ import annotations

import logging
import typing

import mousebender.simple
import requests

from . import base

LOGGER = logging.getLogger(__name__)


class SimpleIndexFinder(
        base.CandidateFinder,
):  # pylint: disable=too-few-public-methods
    """Find candidates in PEP503 simple index."""

    PYPI_BASE_URL = 'https://pypi.org/simple/'

    def __init__(
            self,
            registry: base.Registry,
            candidate_makers: typing.Iterable[base.CandidateMaker],
            base_url: typing.Optional[str] = None,
    ) -> None:
        """Initialize."""
        self._registry = registry
        self._candidate_makers = candidate_makers
        self._base_url = base_url if base_url else self.PYPI_BASE_URL

    def find_candidates(  # pylint: disable=too-complex
            self,
            project_key: base.ProjectKey,
            requirements: typing.Iterable[base.Requirement],
            extras: base.Extras,
    ) -> typing.Iterator[base.Candidate]:
        """Implement abstract."""
        #
        if typing.TYPE_CHECKING:
            Candidates = typing.List[base.Candidate]
            Release = typing.Dict[str, Candidates]
        #
        candidates: typing.Dict[base.Version, Release] = {}
        #
        project_url = '{}{}'.format(self._base_url, project_key)
        project_page = requests.get(project_url).content.decode()
        #
        links = mousebender.simple.parse_archive_links(project_page)
        #
        for link in links:
            candidate = self._make_candidate_from_link(link, extras)
            if candidate:
                is_compatible = candidate.is_compatible(
                    requirements,
                    self._registry.environment
                )
                if is_compatible:
                    release = candidates.setdefault(
                        candidate.release_version,
                        {
                            'built': [],
                            'unbuilt': [],
                        },
                    )
                    #
                    if candidate.is_built:
                        release['built'].append(candidate)
                    else:
                        release['unbuilt'].append(candidate)
        #
        if candidates:
            for version in candidates:
                release = candidates[version]
                for candidate in release['built']:
                    yield candidate
                if not release['built']:
                    for candidate in release['unbuilt']:
                        yield candidate

    def _make_candidate_from_link(
            self,
            distribution_link: mousebender.simple.ArchiveLink,
            extras: base.Extras,
    ) -> typing.Optional[base.Candidate]:
        #
        candidate = None
        #
        if not distribution_link.yanked[0]:
            if not self._is_link_python_incompatible(distribution_link):
                distribution_url = distribution_link.url
                candidate = (
                    self._make_candidate_from_url(distribution_url, extras)
                )
        #
        return candidate

    def _make_candidate_from_url(
            self,
            distribution_url: str,
            extras: base.Extras,
    ) -> typing.Optional[base.Candidate]:
        #
        candidate = None
        #
        for candidate_maker in self._candidate_makers:
            candidate = candidate_maker.make_from_uri(
                self._registry,
                distribution_url,
                extras,
                False,  # is_direct
            )
            if candidate:
                break
        #
        return candidate

    def _is_link_python_incompatible(
            self,
            distribution_link: mousebender.simple.ArchiveLink,
    ) -> bool:
        """Check if link advertises itself as incompatible with this Python."""
        #
        env_python_version = self._registry.environment.python_version
        link_python_specifier = distribution_link.requires_python
        #
        is_incompatible = (env_python_version not in link_python_specifier)
        #
        return is_incompatible


# EOF
