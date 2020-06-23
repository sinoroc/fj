#

"""Functionalities for the 'resolve' command."""

from __future__ import annotations

import logging
import typing
import xml.etree.ElementTree

import html5lib
import packaging
import requests

from . import base

LOGGER = logging.getLogger(__name__)


def _is_link_python_incompatible(
        distribution_link: xml.etree.ElementTree.Element,
        python_version: packaging.version.Version,
) -> bool:
    """Check if link advertises itself as incompatible with this Python."""
    #
    is_incompatible = False
    #
    python_requirement_str = (
        distribution_link.attrib.get('data-requires-python', None)
    )
    if python_requirement_str is not None:
        python_requirement_specifier = (
            packaging.specifiers.SpecifierSet(python_requirement_str)
        )
        if python_requirement_specifier:
            if python_version not in python_requirement_specifier:
                is_incompatible = True
    #
    return is_incompatible


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

    def _get_candidate_from_url(
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

    def _get_candidate_from_link(
            self,
            distribution_link: xml.etree.ElementTree.Element,
            extras: base.Extras,
    ) -> typing.Optional[base.Candidate]:
        #
        candidate = None
        #
        python_version = self._registry.environment.python_version
        is_link_python_incompatible = (
            _is_link_python_incompatible(distribution_link, python_version)
        )
        if not is_link_python_incompatible:
            distribution_url = distribution_link.attrib['href']
            candidate = self._get_candidate_from_url(distribution_url, extras)
        #
        return candidate

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
        project_page = requests.get(project_url).content
        project_page_document = html5lib.parse(
            project_page,
            namespaceHTMLElements=False,
        )
        for distribution_link in project_page_document.findall('.//a'):
            candidate = (
                self._get_candidate_from_link(distribution_link, extras)
            )
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


# EOF
