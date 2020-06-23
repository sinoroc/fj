#

"""Handle candidates from pool."""

from __future__ import annotations

import typing

import importlib.metadata
import packaging

from . import base

if typing.TYPE_CHECKING:
    import pathlib


class _PoolCandidate(base.BaseCandidate):

    def __init__(
            self,
            distribution: importlib.metadata.Distribution,
            extras: base.Extras,
    ):
        super().__init__(extras)
        #
        self._distribution = distribution

    @property
    def is_in_pool(self) -> bool:
        """Implement abstract."""
        return True

    def _get_metadata(self) -> base.Metadata:
        metadata_: base.Metadata = (
            self._distribution.metadata  # type: ignore[assignment]
        )
        return metadata_


def _find_distribution(
        dir_path: pathlib.Path,
) -> typing.Optional[importlib.metadata.Distribution]:
    #
    distribution = None
    #
    dist_info_path = None
    for item in dir_path.glob('*.*-info'):
        if item.is_dir():
            dist_info_path = item
            distribution = importlib.metadata.Distribution.at(dist_info_path)
            break
    #
    return distribution


class PoolCandidateFinder(
        base.CandidateFinder,
):  # pylint: disable=too-few-public-methods
    """Find candidates in the pool."""

    def __init__(self, registry: base.Registry) -> None:
        """Initialize."""
        self._pool_distributions = []
        pool_dir_path = registry.get_pool_dir_path()
        if pool_dir_path and pool_dir_path.is_dir():
            for item in pool_dir_path.iterdir():
                if item.is_dir():
                    distribution = _find_distribution(item)
                    if distribution:
                        self._pool_distributions.append(distribution)

    def find_candidates(
            self,
            project_key: base.ProjectKey,
            requirements: typing.Iterable[base.Requirement],
            extras: base.Extras,
    ) -> typing.Iterator[base.Candidate]:
        """Implement abstract."""
        #
        for distribution in self._pool_distributions:
            distribution_name = distribution.metadata['Name']
            distribution_key = (
                packaging.utils.canonicalize_name(distribution_name)
            )
            if distribution_key == project_key:
                candidate = _PoolCandidate(distribution, extras)
                yield candidate


# EOF
