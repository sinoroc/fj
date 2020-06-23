#

"""Handle 'wheel' distribution files."""

from __future__ import annotations

import abc
import dataclasses
import email.parser
import logging
import typing
import zipfile

import packaging
import pep517.envbuild

from . import base
from . import _distribution

if typing.TYPE_CHECKING:
    import pathlib
    #
    _ProjectKey = typing.Optional[base.ProjectKey]
    _Tags = typing.Optional[base.Tags]
    _Version = typing.Optional[base.Version]
    _FilePathParserResult = typing.Tuple[_ProjectKey, _Version, _Tags]

LOGGER = logging.getLogger(__name__)


class WheelCandidate(
        _distribution.DistFileCandidate,
        metaclass=abc.ABCMeta,
):
    """Abstract candidate for a 'wheel' distribution."""

    def __init__(  # pylint: disable=too-many-arguments
            self,
            registry: base.Registry,
            uri_str: str,
            project_key: base.ProjectKey,
            release_version: base.Version,
            tags: base.Tags,
            extras: base.Extras,
            is_direct: bool,
    ) -> None:
        """Initialize."""
        #
        super().__init__(
            registry,
            uri_str,
            project_key,
            release_version,
            extras,
            is_direct,
        )
        #
        self._tags = tags

    def _get_metadata(self) -> typing.Optional[base.Metadata]:
        metadata_ = get_metadata(self.path)
        return metadata_

    @property
    def is_built(self) -> bool:
        """Override."""
        return True

    def is_compatible(
            self,
            requirements: typing.Iterable[base.Requirement],
            environment: base.Environment,
    ) -> bool:
        """Implement abstract."""
        #
        compatible = (
            super().is_compatible(requirements, environment)
            and
            self._is_tags_compatible(environment)
        )
        #
        return compatible

    def _is_tags_compatible(
            self,
            environment: base.Environment,
    ) -> bool:
        """Check if candidate is compatible with environment."""
        is_compatible = False
        #
        for tag in self._tags:
            if tag in environment.tags:
                is_compatible = True
                break
        #
        return is_compatible


def get_metadata(wheel_path: pathlib.Path) -> typing.Optional[base.Metadata]:
    """Get metadata for a 'wheel' distribution file."""
    #
    metadata = None
    #
    with zipfile.ZipFile(wheel_path) as zip_file:
        for file_name in zip_file.namelist():
            if file_name.endswith(".dist-info/METADATA"):
                email_parser = email.parser.BytesParser()
                metadata = email_parser.parse(
                    zip_file.open(file_name),  # type: ignore[arg-type]
                    headersonly=True,
                )
                break
    #
    return metadata  # type: ignore[return-value]


class CanNotBuildWheel(Exception):
    """Can not build wheel."""


class CanNotFindBuiltWheel(Exception):
    """Can not find the built wheel."""


def build_wheel(
        source_dir_path: pathlib.Path,
        target_dir_path: pathlib.Path,
) -> pathlib.Path:
    """Build a wheel distribution file."""
    #
    wheel_path = None
    #
    LOGGER.info("Building wheel for '%s'...", source_dir_path)
    #
    try:
        wheel_file_name = pep517.envbuild.build_wheel(
            str(source_dir_path),
            str(target_dir_path),
        )
    except Exception:
        raise CanNotBuildWheel(source_dir_path)
    else:
        wheel_path = target_dir_path.joinpath(wheel_file_name)
        if wheel_path.is_file():
            LOGGER.info("Built wheel '%s'.", wheel_path)
        else:
            raise CanNotFindBuiltWheel(wheel_path)
    #
    return wheel_path


class WheelCandidateMaker(base.CandidateMaker):
    """Make candidate for a 'wheel' distribution file."""

    @dataclasses.dataclass
    class ParserResult(base.CandidateMaker.ParserResult):
        """Override."""

        tags: base.Tags

    @classmethod
    def _make(  # pylint: disable=too-many-arguments
            cls,
            registry: base.Registry,
            uri_str: str,
            parser_result: base.CandidateMaker.ParserResult,
            extras: base.Extras,
            is_direct: bool,
    ) -> WheelCandidate:
        #
        parser_result_ = (
            typing.cast(WheelCandidateMaker.ParserResult, parser_result)
        )
        #
        candidate = WheelCandidate(
            registry,
            uri_str,
            parser_result_.project_key,
            parser_result_.release_version,
            parser_result_.tags,
            extras,
            is_direct,
        )
        #
        return candidate

    @classmethod
    def _parse_uri_path(
            cls,
            registry: base.Registry,
            uri_path: pathlib.Path,
    ) -> typing.Optional[ParserResult]:
        #
        parser_result = None
        #
        project_key, release_version, tags = parse_file_path(uri_path)
        #
        if project_key and release_version and tags:
            parser_result = cls.ParserResult(
                project_key,
                release_version,
                tags,
            )
        #
        return parser_result


def parse_file_path(file_path: pathlib.Path) -> _FilePathParserResult:
    """Parse 'wheel' file path to extract project's key, tags and version."""
    #
    project_key = None
    release_version = None
    tags = None
    #
    if file_path.suffixes[-1:] == ['.whl']:
        stem = file_path.stem
        parts = stem.rsplit('-', 5)
        if len(parts) == 5:
            project_label = parts[0]
            version_str = parts[1]
            tag_str = '-'.join(parts[-3:])
            project_key = packaging.utils.canonicalize_name(project_label)
            try:
                release_version = packaging.version.Version(version_str)
            except packaging.version.InvalidVersion:
                pass
            tags = packaging.tags.parse_tag(tag_str)
    #
    return project_key, release_version, tags


# EOF
