#

"""Base functionalities for the dependency solver."""

from __future__ import annotations

import abc
import contextlib
import dataclasses
import pathlib
import platform
import sys
import sysconfig
import tempfile
import typing
import urllib

import appdirs
import packaging.requirements
import packaging.tags
import packaging.utils
import packaging.version

if typing.TYPE_CHECKING:
    import email
    #
    Extra = str
    Extras = typing.Set[Extra]
    Metadata = email.message.EmailMessage
    ProjectKey = packaging.utils.NormalizedName
    Tags = typing.FrozenSet[packaging.tags.Tag]
    Version = packaging.version.Version
    Requirement = packaging.requirements.Requirement


@dataclasses.dataclass
class Environment:
    """Environment information."""

    purelib_dir_path: pathlib.Path
    python_implementation_str: str
    python_processor_str: str
    python_version: Version
    search_path: typing.List[str]
    tags: Tags


class Registry:
    """Registry."""

    def __init__(
            self,
            application_name: str,
            environment: Environment,
            temp_dir_path: pathlib.Path,
    ) -> None:
        """Initialize."""
        self._application_name = application_name
        self._environment = environment
        self._temp_dir_path = temp_dir_path

    @property
    def environment(self) -> Environment:
        """Environment."""
        return self._environment

    def get_distributions_cache_dir_path(self) -> pathlib.Path:
        """Get path to the directory for the cache of distributions."""
        distributions_cache_dir_path = (
            self._get_user_cache_dir_path().joinpath('distributions')
        )
        return distributions_cache_dir_path

    def get_interpreter_dir_path(self) -> pathlib.Path:
        """Get path to the directory specific to the current interpreter."""
        interpreter_key = _get_interpreter_key(self._environment)
        interpreter_dir_path = (
            self._get_user_data_dir_path().joinpath(interpreter_key)
        )
        return interpreter_dir_path

    def get_pool_dir_path(self) -> pathlib.Path:
        """Get path to the directory for the pool."""
        pool_dir_path = self.get_interpreter_dir_path().joinpath('pool')
        return pool_dir_path

    def get_requirement_dir_path(
            self,
            requirement: Requirement,
    ) -> typing.Optional[pathlib.Path]:
        """Get path to the directory containing the requirement."""
        requirement_dir_path = None
        version = _get_locked_requirement_version(requirement)
        if version:
            pool_dir_path = self.get_pool_dir_path()
            requirement_dir_path = pool_dir_path.joinpath(
                '{}-{}'.format(requirement.name, version),
            )
        return requirement_dir_path

    def get_requirement_for_dir_path(
            self,
            requirement_dir_path: pathlib.Path,
    ) -> typing.Optional[Requirement]:
        """Get requirement corresponding to this directory."""
        requirement = None
        pool_dir_path = self.get_pool_dir_path()
        try:
            relative_path = requirement_dir_path.relative_to(pool_dir_path)
        except ValueError:
            pass
        else:
            project_key, version_string = str(relative_path).rsplit('-', 1)
            requirement_str = f'{project_key}=={version_string}'
            requirement = packaging.requirements.Requirement(requirement_str)
        return requirement

    def get_temp_dir_path(self) -> pathlib.Path:
        """Get path to temporary directory."""
        return self._temp_dir_path

    def _get_user_cache_dir_path(self) -> pathlib.Path:
        user_cache_dir_path = (
            pathlib.Path(appdirs.user_cache_dir(self._application_name))
        )
        return user_cache_dir_path

    def _get_user_data_dir_path(self) -> pathlib.Path:
        user_data_dir_path = (
            pathlib.Path(appdirs.user_data_dir(self._application_name))
        )
        return user_data_dir_path


@contextlib.contextmanager
def build_registry(
        application_name: str,
        environment: typing.Optional[Environment] = None,
) -> typing.Iterator[Registry]:
    """Build registry as a context manager."""
    #
    if not environment:
        environment = _get_current_environment()
    #
    with tempfile.TemporaryDirectory() as temp_dir_name:
        temp_dir_path = pathlib.Path(temp_dir_name)
        registry = Registry(application_name, environment, temp_dir_path)
        yield registry


class CanNotReadCandidateMetadata(Exception):
    """Can not read candidate metadata."""


class Candidate(metaclass=abc.ABCMeta):
    """Abstract candidate for dependency solver."""

    @property
    @abc.abstractmethod
    def dependencies(self) -> typing.List[Requirement]:
        """Dependencies."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def extras(self) -> Extras:
        """Extras."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def is_built(self) -> bool:
        """Is built."""
        raise NotImplementedError

    @abc.abstractmethod
    def is_compatible(
            self,
            requirements: typing.Iterable[Requirement],
            environment: Environment,
    ) -> bool:
        """Check if is compatible with environment."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def is_direct(self) -> bool:
        """Is in environment."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def is_in_environment(self) -> bool:
        """Is in environment."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def is_in_pool(self) -> bool:
        """Is in pool."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def metadata(self) -> Metadata:
        """Metadata."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def project_key(self) -> ProjectKey:
        """Canonical project key."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def release_version(self) -> Version:
        """Release version."""
        raise NotImplementedError


class BaseCandidate(Candidate, metaclass=abc.ABCMeta):
    """Abstract base candidate for dependency solver."""

    def __init__(self, extras: Extras) -> None:
        """Initialize."""
        #
        self._extras = extras
        #
        self._dependencies: typing.Optional[typing.List[Requirement]] = None
        self._metadata: typing.Optional[Metadata] = None
        self._project_key: typing.Optional[ProjectKey] = None
        self._release_version: typing.Optional[Version] = None

    def __repr__(self) -> str:
        """Get printable representation."""
        repr_ = (
            f'{self.__class__.__module__}.{self.__class__.__qualname__}'
            f'('
            f'\'{self.project_key}\''
            f', '
            f'{self.release_version}'
            f', '
            f'extras={self.extras}'
            f')'
        )
        return repr_

    def __str__(self) -> str:
        """Get string representation."""
        str_ = (
            f'{self.project_key}-{self.release_version}'
            f'({self.__class__.__qualname__})'
        )
        return str_

    @property
    def dependencies(self) -> typing.List[Requirement]:
        """Implement abstract."""
        if self._dependencies is None:
            self._dependencies = list(self._get_dependencies())
        return self._dependencies

    @property
    def extras(self) -> Extras:
        """Implement abstract."""
        return self._extras

    @property
    def is_built(self) -> bool:
        """Implement abstract."""
        return False

    def is_compatible(
            self,
            requirements: typing.Iterable[Requirement],
            environment: Environment,
    ) -> bool:
        """Implement abstract."""
        return is_candidate_requirements_compatible(self, requirements)

    @property
    def is_direct(self) -> bool:
        """Implement abstract."""
        return False

    @property
    def is_in_environment(self) -> bool:
        """Implement abstract."""
        return False

    @property
    def is_in_pool(self) -> bool:
        """Implement abstract."""
        return False

    @property
    def metadata(self) -> Metadata:
        """Implement abstract."""
        #
        if self._metadata is None:
            self._metadata = self._get_metadata()
            if not self._metadata:
                raise CanNotReadCandidateMetadata(self)
        #
        return self._metadata

    @property
    def project_key(self) -> ProjectKey:
        """Implement abstract."""
        if self._project_key is None:
            project_name = self.metadata['Name']
            self._project_key = packaging.utils.canonicalize_name(project_name)
        return self._project_key

    @property
    def release_version(self) -> Version:
        """Implement abstract."""
        if self._release_version is None:
            version_str = self.metadata['Version']
            self._release_version = packaging.version.Version(version_str)
        return self._release_version

    def _get_dependencies(self) -> typing.Iterator[Requirement]:
        dependencies_: typing.List[str] = (
            self.metadata.get_all('Requires-Dist', [])
        )
        for dependency in dependencies_:
            requirement = packaging.requirements.Requirement(dependency)
            if requirement.marker is None:
                yield requirement
            else:
                for extra in self.extras:
                    if requirement.marker.evaluate({'extra': extra}):
                        yield requirement

    @abc.abstractmethod
    def _get_metadata(self) -> typing.Optional[Metadata]:
        """Get the metadata, or None."""
        raise NotImplementedError


def is_candidate_requirements_compatible(
        candidate: Candidate,
        requirements: typing.Iterable[Requirement],
) -> bool:
    """Check if candidate is compatible with requirements."""
    #
    is_compatible = False
    #
    release_version = candidate.release_version
    project_key = candidate.project_key
    #
    for requirement in requirements:
        key = packaging.utils.canonicalize_name(requirement.name)
        specifiers = requirement.specifier
        if project_key != key or release_version not in specifiers:
            break
    else:
        is_compatible = True
    #
    return is_compatible


class CandidateFinder(  # pylint: disable=too-few-public-methods
        metaclass=abc.ABCMeta,
):
    """Find candidates for dependency resolution."""

    @abc.abstractmethod
    def find_candidates(
            self,
            project_key: ProjectKey,
            requirements: typing.Iterable[Requirement],
            extras: Extras,
    ) -> typing.Iterator[Candidate]:
        """Find candidates."""
        raise NotImplementedError


class CandidateMaker(
        metaclass=abc.ABCMeta,
):
    """Make candidates."""

    @classmethod
    def make_from_direct_requirement(
            cls,
            registry: Registry,
            requirement: Requirement,
            extras: Extras,
    ) -> typing.Optional[Candidate]:
        """Make candidate for a requirement with a URI."""
        uri_str = requirement.url
        candidate = cls.make_from_uri(registry, uri_str, extras, True)
        return candidate

    @classmethod
    def make_from_uri(
            cls,
            registry: Registry,
            uri_str: str,
            extras: Extras,
            is_direct: bool,
    ) -> typing.Optional[Candidate]:
        """Make a candidate for a URI."""
        #
        candidate = None
        #
        parser_result = cls.parse_uri(registry, uri_str)
        #
        if parser_result:
            candidate = cls._make(
                registry,
                uri_str,
                parser_result,
                extras,
                is_direct,
            )
        #
        return candidate

    @classmethod
    @abc.abstractmethod
    def _make(  # pylint: disable=too-many-arguments
            cls,
            registry: Registry,
            uri_str: str,
            parser_result: CandidateMaker.ParserResult,
            extras: Extras,
            is_direct: bool,
    ) -> Candidate:
        """Make a candidate."""
        raise NotImplementedError

    @dataclasses.dataclass
    class ParserResult:
        """Result from parsing."""

        project_key: ProjectKey
        release_version: Version

    @classmethod
    def parse_uri(
            cls,
            registry: Registry,
            uri_str: str,
    ) -> typing.Optional[ParserResult]:
        """Parse a URI."""
        #
        parser_result = None
        #
        uri_parts = urllib.parse.urlparse(uri_str)
        uri_path = pathlib.Path(uri_parts.path)
        #
        parser_result = cls._parse_uri_path(registry, uri_path)
        #
        return parser_result

    @classmethod
    @abc.abstractmethod
    def _parse_uri_path(
            cls,
            registry: Registry,
            uri_path: pathlib.Path
    ) -> typing.Optional[ParserResult]:
        """Parse URI path."""
        raise NotImplementedError


def _get_interpreter_key(environment: Environment) -> str:
    #
    interpreter_key = (
        f'{environment.python_implementation_str}'
        '-'
        f'{environment.python_version.major}'
        '.'
        f'{environment.python_version.minor}'
        '-'
        f'{environment.python_processor_str}'
    )
    #
    return interpreter_key


def _get_locked_requirement_version(
        requirement: Requirement,
) -> typing.Optional[str]:
    #
    version = None
    #
    specifier_set = requirement.specifier
    if len(specifier_set) == 1:
        specifier = next(iter(specifier_set))
        if specifier.operator == '==':  # type: ignore[attr-defined]
            version = specifier.version  # type: ignore[attr-defined]
    #
    return version


def _get_current_environment() -> Environment:
    """Get current environment information."""
    #
    purelib_dir_path = pathlib.Path(sysconfig.get_paths()['purelib'])
    #
    python_implementation_str = platform.python_implementation()
    #
    python_processor_str = platform.processor()
    #
    python_version = packaging.version.Version(platform.python_version())
    #
    search_path = sys.path
    #
    tags = frozenset(packaging.tags.sys_tags())
    #
    environment = Environment(
        purelib_dir_path,
        python_implementation_str,
        python_processor_str,
        python_version,
        search_path,
        tags,
    )
    #
    return environment


# EOF
