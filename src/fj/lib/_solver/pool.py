#

"""Handle candidates from pool."""

from __future__ import annotations

import typing

import importlib.metadata
import packaging

from .. import base

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


def find_distributions(
        registry: base.Registry,
) -> typing.List[importlib.metadata.Distribution]:
    """Get distributions from pool."""
    #
    pool_distributions = []
    #
    pool_dir_path = registry.get_pool_dir_path()
    #
    if pool_dir_path.is_dir():
        for tag_dir_path in pool_dir_path.iterdir():
            tags_str = tag_dir_path.name
            tags = packaging.tags.parse_tag(tags_str)
            for tag in tags:
                if tag_dir_path.is_dir() and tag in registry.environment.tags:
                    tag_distributions = _find_distributions_in_tag_dir(
                        tag_dir_path,
                    )
                    pool_distributions.extend(tag_distributions)
    #
    return pool_distributions


def _find_distributions_in_tag_dir(
        tag_dir_path: pathlib.Path,
) -> typing.List[importlib.metadata.Distribution]:
    #
    distributions = []
    #
    for path in tag_dir_path.iterdir():
        if path.is_dir():
            distribution = find_distribution(path)
            if distribution:
                distributions.append(distribution)
    #
    return distributions


def find_distribution(
        dir_path: pathlib.Path,
) -> typing.Optional[importlib.metadata.Distribution]:
    """Get distribution in the directory."""
    #
    distribution = None
    #
    for item in dir_path.glob('*.dist-info'):
        if item.is_dir():
            distribution = importlib.metadata.Distribution.at(item)
            break
    #
    return distribution


class PoolCandidateFinder(
        base.CandidateFinder,
):  # pylint: disable=too-few-public-methods
    """Find candidates in the pool."""

    def __init__(self, registry: base.Registry) -> None:
        """Initialize."""
        self._registry = registry
        #
        self._pool_distributions = find_distributions(self._registry)

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
                is_compatible = candidate.is_compatible(
                    requirements,
                    self._registry.environment,
                )
                if is_compatible:
                    yield candidate


# EOF
