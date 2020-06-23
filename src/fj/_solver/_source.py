#

"""Handle source code directories as candidates."""

from __future__ import annotations

import functools
import logging
import pathlib
import typing
import urllib

import packaging

from . import base
from . import _wheel

LOGGER = logging.getLogger(__name__)

WHEEL_DIR_NAME = 'built_from_source'


class SourceDirectoryCandidate(
        base.BaseCandidate,
):
    """Candidate for a source directory."""

    def __init__(  # pylint: disable=too-many-arguments
            self,
            registry: base.Registry,
            uri_str: str,
            project_key: base.ProjectKey,
            release_version: base.Version,
            extras: base.Extras,
            is_direct: bool,
    ) -> None:
        """Initialize."""
        #
        super().__init__(extras)
        #
        self._registry = registry
        self._project_key = project_key
        self._uri_str = uri_str
        self._release_version = release_version
        self._is_direct = is_direct
        #
        self._path: typing.Optional[pathlib.Path] = None
        self._source_path: typing.Optional[pathlib.Path] = None

    @property
    def is_direct(self) -> bool:
        """Override."""
        return self._is_direct

    @property
    def path(self) -> pathlib.Path:
        """Get path to installable distribution."""
        if self._path is None:
            self._path = self._get_path()
        return self._path

    @property
    def source_path(self) -> pathlib.Path:
        """Get path to source directory."""
        if self._source_path is None:
            self._source_path = self._get_source_path()
        return self._source_path

    def _get_metadata(self) -> typing.Optional[base.Metadata]:
        metadata_ = _wheel.get_metadata(self.path)
        return metadata_

    def _get_path(self) -> pathlib.Path:
        #
        wheel_dir_path = (
            self._registry.get_temp_dir_path().joinpath(WHEEL_DIR_NAME)
        )
        for item in wheel_dir_path.iterdir():
            project_key, release_version, tags = _wheel.parse_file_path(item)
            if project_key and release_version and tags:
                if (
                        project_key == self.project_key
                        and
                        release_version == self.release_version
                ):
                    wheel_path = item
                    break
        else:
            wheel_path = _wheel.build_wheel(self.source_path, wheel_dir_path)
        #
        return wheel_path

    def _get_source_path(self) -> pathlib.Path:
        #
        uri_parts = urllib.parse.urlparse(self._uri_str)
        source_dir_path = pathlib.Path(uri_parts.path)
        #
        return source_dir_path


class SourceDirectoryCandidateMaker(
        base.CandidateMaker,
):
    """Candidate maker for a source directory."""

    @classmethod
    def _make(  # pylint: disable=too-many-arguments
            cls,
            registry: base.Registry,
            uri_str: str,
            parser_result: base.CandidateMaker.ParserResult,
            extras: base.Extras,
            is_direct: bool,
    ) -> SourceDirectoryCandidate:
        #
        candidate = SourceDirectoryCandidate(
            registry,
            uri_str,
            parser_result.project_key,
            parser_result.release_version,
            extras,
            is_direct,
        )
        return candidate

    @classmethod
    @functools.lru_cache(maxsize=None)
    def _parse_uri_path(
            cls,
            registry: base.Registry,
            uri_path: pathlib.Path,
    ) -> typing.Optional[base.CandidateMaker.ParserResult]:
        """Parse a URI."""
        #
        parser_result = None
        #
        if uri_path.is_dir():
            target_dir_path = (
                registry.get_temp_dir_path().joinpath(WHEEL_DIR_NAME)
            )
            target_dir_path.mkdir()
            wheel_path = _wheel.build_wheel(uri_path, target_dir_path)
            metadata = _wheel.get_metadata(wheel_path)
            if metadata:
                parser_result = cls.ParserResult(
                    packaging.utils.canonicalize_name(metadata['Name']),
                    packaging.version.Version(metadata['Version']),
                )
        #
        return parser_result


# EOF
