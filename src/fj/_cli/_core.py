#

"""Core functionalities."""

from __future__ import annotations

import pathlib
import typing

from .. import ext
from .. import lib
from .. import _meta
from .. import _utils

DIRECT_URI_CANDIDATE_MAKERS = [
    ext.source.SourceDirectoryCandidateMaker(),
    ext.sdist.SdistCandidateMaker(),
    lib.wheel.WheelCandidateMaker(),
]

INSTALLERS: typing.List[lib.base.Installer] = [
    ext.pip.PipInstaller(),
]

WHEEL_BUILDERS = [
    lib.wheel.Pep517WheelBuilder(),
    ext.pip.PipWheelBuilder(),
]


def cache_list() -> typing.List[pathlib.Path]:
    """List cached distributions."""
    with lib.base.build_registry(_meta.PROJECT_NAME) as registry:
        cached_distributions = lib.cache.list_(registry)
    return cached_distributions


def install(
        requirements_strs: typing.Iterable[str],
        skip_dependencies: bool,
) -> None:
    """Install things."""
    with lib.base.build_registry(_meta.PROJECT_NAME) as registry:
        registry.direct_uri_candidate_makers = DIRECT_URI_CANDIDATE_MAKERS
        registry.installers = INSTALLERS
        registry.wheel_builders = WHEEL_BUILDERS
        requirements = lib.parser.parse(registry, requirements_strs)
        lib.install.install(registry, requirements, [], skip_dependencies)


def links_add(requirements_strs: typing.Iterable[str]) -> None:
    """Add links to requirements."""
    with lib.base.build_registry(_meta.PROJECT_NAME) as registry:
        registry.direct_uri_candidate_makers = DIRECT_URI_CANDIDATE_MAKERS
        requirements = lib.parser.parse(registry, requirements_strs)
        lib.links.add(registry, requirements)


def links_list() -> typing.List[lib.base.Requirement]:
    """List links."""
    with lib.base.build_registry(_meta.PROJECT_NAME) as registry:
        links = lib.links.list_(registry)
    return links


def links_remove(requirements_strs: typing.Iterable[str]) -> None:
    """Remove links to requirements."""
    with lib.base.build_registry(_meta.PROJECT_NAME) as registry:
        requirements = lib.parser.parse(registry, requirements_strs)
        lib.links.remove(registry, requirements)


def pip_install(
        requirements_strs: typing.Iterable[str],
        editable_requirement_strs: typing.Iterable[str],
        no_deps: bool,
) -> None:
    """Emulate 'pip install'."""
    with lib.base.build_registry(_meta.PROJECT_NAME) as registry:
        registry.direct_uri_candidate_makers = DIRECT_URI_CANDIDATE_MAKERS
        registry.installers = INSTALLERS
        registry.wheel_builders = WHEEL_BUILDERS
        requirements = lib.parser.parse(registry, requirements_strs)
        editable_requirements = (
            lib.parser.parse(registry, editable_requirement_strs)
        )
        lib.install.install(
            registry,
            requirements,
            editable_requirements,
            no_deps,
        )


def pool_add(requirements_strs: typing.Iterable[str]) -> None:
    """Resolve requirements and add elected candidates to pool."""
    with lib.base.build_registry(_meta.PROJECT_NAME) as registry:
        registry.direct_uri_candidate_makers = DIRECT_URI_CANDIDATE_MAKERS
        registry.installers = INSTALLERS
        registry.wheel_builders = WHEEL_BUILDERS
        requirements = lib.parser.parse(registry, requirements_strs)
        lib.pool.add(registry, requirements)


def pool_list() -> typing.List[lib.base.Requirement]:
    """List projects in pool."""
    with lib.base.build_registry(_meta.PROJECT_NAME) as registry:
        pooled_projects = lib.pool.list_(registry)
    return pooled_projects


def pool_remove(requirements_strs: typing.Iterable[str]) -> None:
    """Remove from pool."""
    with lib.base.build_registry(_meta.PROJECT_NAME) as registry:
        requirements = lib.parser.parse(registry, requirements_strs)
        lib.pool.remove(registry, requirements)


def solve(requirements_strs: typing.Iterable[str]) -> None:
    """Resolve requirements."""
    with lib.base.build_registry(_meta.PROJECT_NAME) as registry:
        registry.direct_uri_candidate_makers = DIRECT_URI_CANDIDATE_MAKERS
        registry.wheel_builders = WHEEL_BUILDERS
        requirements = lib.parser.parse(registry, requirements_strs)
        lib.solve.solve(registry, requirements, False)


def ve_create(venv_dir_str: str) -> None:
    """Create virtual environment."""
    venv_dir_path = pathlib.Path(venv_dir_str).resolve()
    _utils.venv_wrapper.ve_create(venv_dir_path)


# EOF
