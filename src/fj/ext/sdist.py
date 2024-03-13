#

"""Handle 'sdist' source distribution files."""

from __future__ import annotations

import abc
import logging
import pathlib
import tarfile
import tempfile
import typing
import zipfile

import packaging.utils
import packaging.version

from .. import lib

LOGGER = logging.getLogger(__name__)

WHEEL_DIR_PATH = 'built_from_sdist'


class SdistCandidate(
        lib.distribution.DistFileCandidate,
        metaclass=abc.ABCMeta,
):
    """Abstract candidate for a 'sdist' source distribution file."""

    def _get_metadata(self) -> typing.Optional[lib.base.Metadata]:
        #
        metadata_ = lib.wheel.get_metadata(self.path_built)
        #
        return metadata_

    def _get_path_built(self) -> pathlib.Path:
        #
        wheel_path = self._extract_and_build()
        #
        return wheel_path

    def _extract_and_build(self) -> pathlib.Path:
        #
        wheel_path = None
        #
        with tempfile.TemporaryDirectory() as extraction_dir_path:
            LOGGER.info("Extracting %s to %s", self.path, extraction_dir_path)
            #
            if self.path.suffixes[-1:] == ['.zip']:
                with zipfile.ZipFile(self.path) as zip_file:
                    zip_file.extractall(extraction_dir_path)
            elif self.path.suffixes[-2:] == ['.tar', '.gz']:
                with tarfile.open(self.path) as tar_file:
                    tar_file.extractall(extraction_dir_path)
            #
            for item in pathlib.Path(extraction_dir_path).iterdir():
                if item.is_dir():
                    source_dir_path = item
                    wheel_path = self._build_wheel(source_dir_path)
                    break
        #
        if wheel_path is None:
            raise Exception
        #
        return wheel_path

    def _build_wheel(
            self,
            source_dir_path: pathlib.Path,
    ) -> pathlib.Path:
        #
        is_cache_possible = not self.is_direct
        #
        if is_cache_possible:
            target_dir_path = (
                self._registry.get_distributions_cache_dir_path()
            )
        else:
            target_dir_path = (
                self._registry.get_temp_dir_path().joinpath(WHEEL_DIR_PATH)
            )
        #
        wheel_path = lib.wheel.build_wheel(
            self._registry,
            source_dir_path,
            target_dir_path,
        )
        #
        return wheel_path


class SdistCandidateMaker(lib.base.CandidateMaker):
    """Make candidates for 'sdist' source distribution files."""

    @classmethod
    def _make(  # pylint: disable=too-many-arguments
            cls,
            registry: lib.base.Registry,
            uri_str: str,
            parser_result: lib.base.CandidateMaker.ParserResult,
            extras: lib.base.Extras,
            is_direct: bool,
    ) -> SdistCandidate:
        #
        candidate = SdistCandidate(
            registry,
            uri_str,
            parser_result.project_key,
            parser_result.release_version,
            extras,
            is_direct,
        )
        #
        return candidate

    @classmethod
    def _parse_uri_path(
            cls,
            registry: lib.base.Registry,
            uri_path: pathlib.Path,
    ) -> typing.Optional[lib.base.CandidateMaker.ParserResult]:
        #
        parser_result = None
        #
        project_key = None
        release_version = None
        #
        stem = None
        if uri_path.suffixes[-1:] == ['.zip']:
            stem = uri_path.name[:-4]
        elif uri_path.suffixes[-2:] == ['.tar', '.gz']:
            stem = uri_path.name[:-7]
        #
        if stem:
            parts = stem.rsplit('-', 1)
            if len(parts) == 2:
                project_label = parts[0]
                version_str = parts[1]
                project_key = packaging.utils.canonicalize_name(project_label)
                try:
                    release_version = packaging.version.Version(version_str)
                except packaging.version.InvalidVersion:
                    pass
        #
        if project_key and release_version:
            parser_result = cls.ParserResult(
                project_key,
                release_version,
            )
        #
        return parser_result


# EOF
