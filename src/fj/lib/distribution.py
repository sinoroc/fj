#

"""Distribution file candidate."""

from __future__ import annotations

import abc
import logging
import pathlib
import typing
import urllib

import requests

from . import base

LOGGER = logging.getLogger(__name__)


class DistFileCandidate(
        base.BaseCandidate,
        metaclass=abc.ABCMeta,
):
    """Abstract candidate for a distribution file."""

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
        self._uri_str = uri_str
        self._project_key = project_key
        self._release_version = release_version
        self._is_direct = is_direct
        #
        self._path: typing.Optional[pathlib.Path] = None
        self._path_built: typing.Optional[pathlib.Path] = None

    @property
    def is_direct(self) -> bool:
        """Override."""
        return self._is_direct

    @property
    def path(self) -> pathlib.Path:
        """Path to distribution file."""
        if self._path is None:
            self._path = self._get_path()
        return self._path

    @property
    def path_built(self) -> pathlib.Path:
        """Path to built distribution file.

        Could be the same path if the candidate is already a built
        distribution.
        """
        if self._path_built is None:
            self._path_built = self._get_path_built()
        return self._path_built

    @abc.abstractmethod
    def _get_path_built(self) -> pathlib.Path:
        """Get the path to built distribution file."""
        raise NotImplementedError

    def _get_path(self) -> pathlib.Path:
        #
        distribution_path = None
        #
        uri_parts = urllib.parse.urlparse(self._uri_str)
        file_path = pathlib.Path(uri_parts.path)
        #
        is_local = uri_parts.scheme == 'file'
        #
        if is_local:
            distribution_path = file_path
        else:
            file_name = file_path.name
            cache_dir_path = self._registry.get_distributions_cache_dir_path()
            maybe_distribution_path = cache_dir_path.joinpath(file_name)
            if maybe_distribution_path.is_file():
                distribution_path = maybe_distribution_path
            else:
                distribution_path = self._add_to_cache(maybe_distribution_path)
        #
        return distribution_path

    def _add_to_cache(
            self,
            destination_path: pathlib.Path,
    ) -> pathlib.Path:
        #
        distribution_path = None
        #
        parent_dir_path = destination_path.parent
        if not parent_dir_path.is_dir():
            LOGGER.info(
                "Creating distribution cache directory: %s",
                parent_dir_path,
            )
            parent_dir_path.mkdir(parents=True)
        #
        LOGGER.info(
            "Caching distribution from '%s' to '%s'",
            self._uri_str,
            destination_path,
        )
        with open(destination_path, 'wb') as distribution_file:
            get_request = requests.get(self._uri_str, stream=True)
            for chunk in get_request.iter_content(chunk_size=128):
                distribution_file.write(chunk)
            distribution_path = destination_path
        #
        return distribution_path


# EOF
