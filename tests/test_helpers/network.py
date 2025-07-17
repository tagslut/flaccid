"""Utilities for mocking aiohttp sessions in tests."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

import pytest
from aioresponses import aioresponses
from aioresponses.core import aioresponses as AioResponses


@contextmanager
def mocked_session() -> Iterator[AioResponses]:
    """Context manager that intercepts aiohttp requests.

    Any request performed using :mod:`aiohttp` will be captured by the
    returned :class:`AioResponses` instance. Unregistered requests raise
    an assertion error to guarantee tests remain offline.
    """
    with aioresponses() as m:
        yield m


@pytest.fixture(autouse=True)
def block_aiohttp_requests() -> Iterator[AioResponses]:
    """Automatically prevent real network requests in tests."""
    with aioresponses() as m:
        yield m
