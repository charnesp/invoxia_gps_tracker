"""Helpers for tests."""
import json
import pathlib
from importlib import import_module
from typing import Any, Dict, Optional, Type

import aioresponses
import attrs
import requests_mock


def get_fixture_path(filename: str) -> pathlib.Path:
    """Get path of a fixture."""
    return pathlib.Path(__file__).parent.joinpath("fixtures", filename)


def _exception_converter(val: str) -> Type[Exception]:
    """Convert a str designating a package exception to its type."""
    mod_path, cls_name = val.rsplit(".", 1)
    module = import_module(mod_path)
    return getattr(module, cls_name)


@attrs.define()
class RequestFixture:
    """Structure of a request answer fixture."""

    url: str = attrs.field(validator=attrs.validators.instance_of(str))
    status: Optional[int] = attrs.field(
        validator=attrs.validators.optional(attrs.validators.instance_of(int)),
        default=None,
    )
    content: Optional[str] = attrs.field(
        validator=attrs.validators.optional(attrs.validators.instance_of(str)),
        default=None,
    )
    exception: Optional[Type[Exception]] = attrs.field(
        converter=attrs.converters.optional(_exception_converter), default=None
    )
    exception_msg: Optional[str] = attrs.field(
        validator=attrs.validators.optional(attrs.validators.instance_of(str)),
        default=None,
    )


class AiohttpMock:
    """Class serving as context manager for async connections."""

    def __init__(self, *fixtures: str):
        """Store fixture options."""
        self.opts = []
        for fixture in fixtures:
            with get_fixture_path(fixture).open("r") as fp:
                data = json.load(fp)
            self.opts.append(self._opts(RequestFixture(**data)))
        self.context = aioresponses.aioresponses()

    @staticmethod
    def _opts(fixture: RequestFixture) -> Dict[str, Any]:
        """Generate options for the context get method."""
        opts: Dict[str, Any] = {"url": fixture.url}
        if fixture.status is not None:
            opts["status"] = fixture.status

        if fixture.content is not None:
            opts["body"] = fixture.content

        if fixture.exception is not None:
            msg = None if fixture.exception_msg is None else fixture.exception_msg
            opts["exception"] = fixture.exception(msg)

        return opts

    def __enter__(self):
        """Mock aiohttp methods."""
        self.context.start()
        for opt in self.opts:
            self.context.get(**opt)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close mock context for aiohttp."""
        self.context.stop()


class RequestsMock:
    """Class serving as context manager for sync connections."""

    def __init__(self, *fixtures: str):
        """Store fixture options."""
        self.opts = []
        for fixture in fixtures:
            with get_fixture_path(fixture).open("r") as fp:
                data = json.load(fp)
            self.opts.append(self._opts(RequestFixture(**data)))
        self.context = requests_mock.Mocker()

    @staticmethod
    def _opts(fixture: RequestFixture) -> Dict[str, Any]:
        """Generate options for the context get method."""
        opts: Dict[str, Any] = {"url": fixture.url}
        if fixture.status is not None:
            opts["status_code"] = fixture.status

        if fixture.content is not None:
            opts["text"] = fixture.content

        if fixture.exception is not None:
            msg = None if fixture.exception_msg is None else fixture.exception_msg
            opts["exc"] = fixture.exception(msg)

        return opts

    def __enter__(self):
        """Mock aiohttp methods."""
        self.context.start()
        for opt in self.opts:
            self.context.get(**opt)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close mock context for aiohttp."""
        self.context.stop()
