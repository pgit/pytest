#!/usr/bin/python3
import pytest
from aiohttp import web


async def hello(request):
    peername = request.transport.get_extra_info('peername')
    if peername is None:
        return web.Response(body=f"Hello, stranger!")
    host, port = peername
    return web.Response(body=f"Hello, {host}:{port}!")

def create_app():
    app = web.Application()
    app.router.add_route("GET", "/", hello)
    return app

@pytest.mark.asyncio
async def test_server(aiohttp_server, aiohttp_client):
    app = create_app()
    server = await aiohttp_server(app, port=38511)
    client = await aiohttp_client(server)
    assert client.port == 38511
    resp = await client.get("/")
    assert resp.status == 200
    text = await resp.text()
    print(text)
    assert "Hello," in text
