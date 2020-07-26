#

"""Dependency solver."""

from __future__ import annotations

import logging
import typing

import resolvelib

from . import _solver

if typing.TYPE_CHECKING:
    from . import base

LOGGER = logging.getLogger(__name__)


def _solve(
        registry: base.Registry,
        finders: typing.Iterable[base.CandidateFinder],
        requirements: typing.Iterable[base.Requirement],
        skip_depencencies: bool,
) -> typing.Optional[resolvelib.resolvers.Result]:
    #
    resolution = None
    #
    provider = _solver.provider.Provider(registry, finders, skip_depencencies)
    reporter = resolvelib.BaseReporter()
    solver = resolvelib.Resolver(provider, reporter)
    #
    try:
        resolution = solver.resolve(requirements)
    except resolvelib.resolvers.ResolutionImpossible:
        pass
    #
    if resolution:
        _display_resolution(requirements, resolution)
    #
    return resolution


def _display_resolution(
        requirements: typing.Iterable[base.Requirement],
        resolution: resolvelib.resolvers.Result,
) -> None:
    print("--- Requirements ---")
    for requirement in requirements:
        print(f"{requirement}")
    print()
    print("--- Pinned Candidates ---")
    for candidate in resolution.mapping.values():
        print(f"{candidate}")
    print()
    print("--- Dependency Graph ---")
    for name in resolution.graph:
        targets = ", ".join(resolution.graph.iter_children(name))
        print(f"{name} -> {targets}")


def solve_for_pool(
        registry: base.Registry,
        requirements: typing.Iterable[base.Requirement],
        skip_depencencies: bool,
) -> resolvelib.resolvers.Result:
    """Solve dependency for the requirements."""
    finders = [
        _solver.pool.PoolCandidateFinder(registry),
        _solver.pep503.SimpleIndexFinder(registry),
    ]
    resolution = _solve(registry, finders, requirements, skip_depencencies)
    return resolution


def solve_for_environment(
        registry: base.Registry,
        requirements: typing.Iterable[base.Requirement],
        skip_depencencies: bool,
) -> resolvelib.resolvers.Result:
    """Solve dependency for the requirements."""
    finders = [
        _solver.direct.DirectCandidateFinder(registry, requirements),
        _solver.active.ActiveFinder(registry),
        _solver.pool.PoolCandidateFinder(registry),
    ]
    resolution = _solve(registry, finders, requirements, skip_depencencies)
    return resolution


def solve(
        registry: base.Registry,
        requirements: typing.Iterable[base.Requirement],
        skip_depencencies: bool,
) -> resolvelib.resolvers.Result:
    """Solve dependency for the requirements."""
    finders = [
        _solver.direct.DirectCandidateFinder(registry, requirements),
        _solver.active.ActiveFinder(registry),
        _solver.pool.PoolCandidateFinder(registry),
        _solver.pep503.SimpleIndexFinder(registry),
    ]
    resolution = _solve(registry, finders, requirements, skip_depencencies)
    return resolution


# EOF
