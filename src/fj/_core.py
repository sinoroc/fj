#

"""Core functionalities."""

from __future__ import annotations

import pathlib
import typing

from . import _cache
from . import _install
from . import _links
from . import _meta
from . import _pool
from . import _solver
from . import _venv


def cache_list() -> typing.List[pathlib.Path]:
    """List cached distributions."""
    with _solver.base.build_registry(_meta.PROJECT_NAME) as registry:
        cached_distributions = _cache.list_(registry)
    return cached_distributions


def install(
        requirements_strs: typing.Iterable[str],
        skip_dependencies: bool,
) -> None:
    """Install things."""
    with _solver.base.build_registry(_meta.PROJECT_NAME) as registry:
        requirements = _solver.parser.parse(registry, requirements_strs)
        _install.install(registry, requirements, [], skip_dependencies)


def links_add(requirements_strs: typing.Iterable[str]) -> None:
    """Add links to requirements."""
    with _solver.base.build_registry(_meta.PROJECT_NAME) as registry:
        requirements = _solver.parser.parse(registry, requirements_strs)
        _links.add(registry, requirements)


def links_list() -> typing.List[_solver.base.Requirement]:
    """List links."""
    with _solver.base.build_registry(_meta.PROJECT_NAME) as registry:
        links = _links.list_(registry)
    return links


def links_remove(requirements_strs: typing.Iterable[str]) -> None:
    """Remove links to requirements."""
    with _solver.base.build_registry(_meta.PROJECT_NAME) as registry:
        requirements = _solver.parser.parse(registry, requirements_strs)
        _links.remove(registry, requirements)


def pip_install(
        requirements_strs: typing.Iterable[str],
        editable_requirement_strs: typing.Iterable[str],
        no_deps: bool,
) -> None:
    """Emulate 'pip install'."""
    with _solver.base.build_registry(_meta.PROJECT_NAME) as registry:
        requirements = _solver.parser.parse(registry, requirements_strs)
        editable_requirements = (
            _solver.parser.parse(registry, editable_requirement_strs)
        )
        _install.install(
            registry,
            requirements,
            editable_requirements,
            no_deps,
        )


def pool_add(requirements_strs: typing.Iterable[str]) -> None:
    """Resolve requirements and add elected candidates to pool."""
    with _solver.base.build_registry(_meta.PROJECT_NAME) as registry:
        requirements = _solver.parser.parse(registry, requirements_strs)
        _pool.add(registry, requirements)


def pool_list() -> typing.List[_solver.base.Requirement]:
    """List projects in pool."""
    with _solver.base.build_registry(_meta.PROJECT_NAME) as registry:
        pooled_projects = _pool.list_(registry)
    return pooled_projects


def pool_remove(requirements_strs: typing.Iterable[str]) -> None:
    """Remove from pool."""
    with _solver.base.build_registry(_meta.PROJECT_NAME) as registry:
        requirements = _solver.parser.parse(registry, requirements_strs)
        _pool.remove(registry, requirements)


def solve(requirements_strs: typing.Iterable[str]) -> None:
    """Resolve requirements."""
    with _solver.base.build_registry(_meta.PROJECT_NAME) as registry:
        requirements = _solver.parser.parse(registry, requirements_strs)
        _solver.solve.solve(registry, requirements, False)


def ve_create(venv_dir_str: str) -> None:
    """Create virtual environment."""
    venv_dir_path = pathlib.Path(venv_dir_str).resolve()
    _venv.ve_create(venv_dir_path)


# EOF
