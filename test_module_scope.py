#!/usr/bin/python3
import asyncio
import aiohttp
from typing import Any, Dict, Optional, Type, Union
from typing import Any, Awaitable, Callable, Dict, Generator, Optional, Type, Union


import pytest_aiohttp
import pytest_asyncio
from aiohttp.test_utils import TestServer, TestClient
from aiohttp.web import Application, Response
from aiohttp.test_utils import BaseTestServer, TestClient, TestServer

AiohttpClient = Callable[[Union[Application, BaseTestServer]], Awaitable[TestClient]]

import pytest

#
# https://pypi.org/project/pytest-asyncio/
#
# Usally, asyncio fixtures are 'function' scope, meaning that the event loop and anything
# else running on it is created and teared down for each test.
#
# If you want to have e.g. a HTTP server running in background covering multiple tests, you
# need to re-define the event_loop fixture to 'module' (or even 'session') scope as well.
#
@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()    
    yield loop
    loop.close()

COUNTER=0
async def handler(request):
    global COUNTER
    COUNTER += 1
    return Response(body=f"This is request #{COUNTER}")

@pytest_asyncio.fixture(scope="module")
async def module_scoped_server():
    app = Application()
    app.router.add_route("GET", "/", handler)
    server = TestServer(app)
    await server.start_server()
    yield server
    await server.close()

#
# We can't use the aiohttp_client fixture together with our custom module scoped server,
# as the client will also stop the server it has been passed when it is closed.
#
@pytest.mark.asyncio
async def test_module_1(module_scoped_server, counter):
    async with aiohttp.ClientSession() as session:
        async with session.get(module_scoped_server.make_url("/")) as resp:
            text = await resp.text()
            assert f"#{counter}" in text

#
# Parametrized "counter" fixture
#
def pytest_generate_tests(metafunc):
    if "counter" in metafunc.fixturenames:
        metafunc.parametrize("counter", range(1, 20))
