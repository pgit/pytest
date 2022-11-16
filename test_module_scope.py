#!/usr/bin/python3
import asyncio

import aiohttp
import pytest_asyncio
from aiohttp.test_utils import TestServer
from aiohttp.web import Application, Response

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

#
# For testing, make a server that returns a response with a counter.
# Also, return the contents of a request header in a future.
#
FUTURE=None
COUNTER=0
async def handler(request:aiohttp.ClientRequest):
    global COUNTER
    global FUTURE
    COUNTER += 1
    assert FUTURE
    FUTURE.set_result(f"{COUNTER}={request.headers['X-Counter']}")
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
async def test_counter(module_scoped_server, counter):
    async with aiohttp.ClientSession() as session:
        global FUTURE
        FUTURE = asyncio.get_event_loop().create_future()
        async with session.get(module_scoped_server.make_url("/"), headers={'X-Counter':f"{counter}"}) as resp:
            text = await resp.text()
            assert f"#{counter}" in text
        
        global COUNTER
        assert await FUTURE == f"{COUNTER}={COUNTER}"
        

# Parametrized "counter" fixture, will run test 'test_counter' with counter=1, 2, ...
def pytest_generate_tests(metafunc):
    if "counter" in metafunc.fixturenames:
        metafunc.parametrize("counter", range(1, 5))
