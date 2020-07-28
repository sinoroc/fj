#

"""Virtual environments."""

from __future__ import annotations

import typing
import venv

if typing.TYPE_CHECKING:
    import pathlib
    import types
    #
    VenvContext = types.SimpleNamespace


class _EnvBuilder(venv.EnvBuilder):

    def __init__(  # type: ignore[no-untyped-def]
            self,
            *args,
            **kwargs,
    ) -> None:
        """Initialize."""
        self.context: typing.Optional[VenvContext] = None
        super().__init__(*args, **kwargs)

    def post_setup(self, context: VenvContext) -> None:
        """Override."""
        self.context = context


def create_venv(venv_dir_path: pathlib.Path) -> typing.Optional[VenvContext]:
    """Create a virtual environment."""
    builder = _EnvBuilder(with_pip=True)
    builder.create(str(venv_dir_path))
    context = builder.context
    return context


def ve_create(venv_dir_path: pathlib.Path) -> None:
    """Create a virtual environment."""
    create_venv(venv_dir_path)


# EOF
