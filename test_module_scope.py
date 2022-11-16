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

async def handle_echo(reader, writer):
    data = await reader.read(100)
    message = data.decode()
    addr = writer.get_extra_info('peername')

    print(f"Received {message!r} from {addr!r}")

    print(f"Send: {message!r}")
    writer.write(data)
    await writer.drain()

    print("Close the connection")
    writer.close()

@pytest_asyncio.fixture(scope="module")
async def x2_receiver(unused_tcp_port):
    server = await asyncio.start_server(handle_echo, '127.0.0.1', unused_tcp_port)

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
        metafunc.parametrize("counter", range(1, 5))
