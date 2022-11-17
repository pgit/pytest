#!/usr/bin/python3
import asyncio

import pytest_asyncio

import pytest


#
# Module-scoped event loop
#
@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

#
# Module-scoped TCP server
#
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
async def echo_server():
    server = await asyncio.start_server(handle_echo, '127.0.0.1')
    assert server.sockets
    yield server
    server.close()


#
# TCP test client
#
@pytest.mark.asyncio
async def test_tcp(echo_server: asyncio.Server, counter):
    socket = echo_server.sockets[0]
    reader, writer = await asyncio.open_connection(*socket.getsockname())
    msg = f"Hello World #{counter}!\n"
    writer.write(msg.encode())
    await writer.drain()
    assert msg == (await reader.readline()).decode()

# Parametrized "counter" fixture, will run test 'test_counter' with counter=1, 2, ...
def pytest_generate_tests(metafunc):
    if "counter" in metafunc.fixturenames:
        metafunc.parametrize("counter", range(1, 5))
