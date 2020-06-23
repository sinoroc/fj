#

"""Parse requirement strings into Requirement objects."""

from __future__ import annotations

import abc
import logging
import pathlib
import re
import typing
import urllib

import packaging

from . import _sdist
from . import _source
from . import _wheel

if typing.TYPE_CHECKING:
    from . import base

LOGGER = logging.getLogger(__name__)

DIRECT_URI_CANDIDATE_MAKERS = {
    _source.SourceDirectoryCandidateMaker(),
    _sdist.SdistCandidateMaker(),
    _wheel.WheelCandidateMaker(),
}


class CanNotParseRequirement(Exception):
    """Can not parse requirement string."""


class RequirementParser(
        metaclass=abc.ABCMeta,
):  # pylint: disable=too-few-public-methods
    """Parse requirement from string."""

    @abc.abstractmethod
    def parse(
            self,
            registry: base.Registry,
            requirement_str: str,
    ) -> typing.Optional[base.Requirement]:
        """Parse requirement from string."""
        raise NotImplementedError


class Pep508RequirementParser(
        RequirementParser,
):  # pylint: disable=too-few-public-methods
    """Parse requirement from a PEP 508 valid string."""

    def parse(
            self,
            registry: base.Registry,
            requirement_str: str,
    ) -> typing.Optional[base.Requirement]:
        """Implement abstract."""
        requirement = None
        try:
            requirement = packaging.requirements.Requirement(requirement_str)
        except packaging.requirements.InvalidRequirement:
            pass
        return requirement


class _BlobParser(  # pylint: disable=too-few-public-methods
        metaclass=abc.ABCMeta,
):

    @staticmethod
    @abc.abstractmethod
    def parse(blob_str: str) -> typing.Optional[str]:
        """Parse a blob string into a canonical URI."""
        raise NotImplementedError


class _LocalPathParser(  # pylint: disable=too-few-public-methods
        _BlobParser,
):

    @staticmethod
    def parse(blob_str: str) -> typing.Optional[str]:
        """Implement abstract."""
        uri_str = None
        if not urllib.parse.urlparse(blob_str).scheme:
            file_path = pathlib.Path(blob_str).resolve()
            uri_parts = urllib.parse.urlparse(f'file://{file_path}')
            uri_str = urllib.parse.urlunparse(uri_parts)
        return uri_str


class _UriParser(  # pylint: disable=too-few-public-methods
        _BlobParser,
):

    @staticmethod
    def parse(blob_str: str) -> typing.Optional[str]:
        """Implement abstract."""
        uri_str = None
        uri_parts = urllib.parse.urlparse(blob_str)
        uri_schemes = [
            'file',
            'http',
            'https',
        ]
        if uri_parts.scheme in uri_schemes:
            uri_str = urllib.parse.urlunparse(uri_parts)
        return uri_str


class DirectUriRequirementParser(  # pylint: disable=too-few-public-methods
        RequirementParser,
):
    """Parse requirement from a string (maybe URL, directory, or file path)."""

    # We are trying to parse what 'tox' provides to 'pip'.
    # Might look like this: '/path/to/Thing-0.0.0.dev0.tar.gz[test,dev]'
    # Not sure exactly what format it is. Is there a PEP?

    def __init__(
            self,
            candidate_makers: typing.Iterable[base.CandidateMaker],
    ) -> None:
        """Initialize."""
        #
        self._candidate_makers = candidate_makers
        #
        self._blob_parsers = [
            _LocalPathParser,
            _UriParser,
        ]

    def _parse_uri_and_extras(
            self,
            requirement_str: str,
    ) -> typing.Tuple[typing.Optional[str], typing.Optional[base.Extras]]:
        """Get URI and extras from URI."""
        #
        uri_str = None
        extras = None
        #
        regex = re.compile(r'([^\[]+)(\[.*?\])*')
        match = regex.fullmatch(requirement_str)
        if match:
            blob_str = match.group(1)
            maybe_extras_str = match.group(2)
            #
            if maybe_extras_str:
                fake_req_str = f'FAKE{maybe_extras_str}'
                fake_req = packaging.requirements.Requirement(fake_req_str)
                if fake_req:
                    extras = fake_req.extras
            else:
                extras = set()
            #
            if blob_str:
                for blob_parser in self._blob_parsers:
                    uri_str = blob_parser.parse(blob_str)
                    if uri_str:
                        break
        #
        return uri_str, extras

    def parse(
            self,
            registry: base.Registry,
            requirement_str: str,
    ) -> typing.Optional[base.Requirement]:
        """Parse as a URI to a distribution file and make a Requirement."""
        #
        requirement = None
        #
        uri_str, extras = self._parse_uri_and_extras(requirement_str)
        #
        if uri_str and extras is not None:
            for candidate_maker in self._candidate_makers:
                parser_result = candidate_maker.parse_uri(registry, uri_str)
                if parser_result:
                    project_key = parser_result.project_key
                    release_version = parser_result.release_version
                    req_str = f'{project_key}=={release_version}'
                    requirement = packaging.requirements.Requirement(req_str)
                    requirement.extras = extras
                    requirement.url = uri_str
                    break
        #
        return requirement


def parse(
        registry: base.Registry,
        requirement_strs: typing.Iterable[str],
) -> typing.List[base.Requirement]:
    """Parse requirement strings into Requirement objects."""
    #
    requirements = []
    #
    requirement_parsers = [
        Pep508RequirementParser(),
        DirectUriRequirementParser(DIRECT_URI_CANDIDATE_MAKERS),
    ]
    #
    for requirement_str in requirement_strs:
        for parser in requirement_parsers:
            requirement = parser.parse(registry, requirement_str)
            if requirement:
                requirements.append(requirement)
                break
        else:
            raise CanNotParseRequirement(requirement_str)
    #
    LOGGER.info("requirements: %s", requirements)
    return requirements


# EOF
