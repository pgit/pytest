# pytest

[![Python application](https://github.com/pgit/pytest/actions/workflows/python-app.yml/badge.svg)](https://github.com/pgit/pytest/actions/workflows/python-app.yml)

This repo contains some experiments with [pytest](https://docs.pytest.org/en/7.2.x/) and [pytest-asyncio](https://pypi.org/project/pytest-asyncio/).

The goal was to have a TCP or HTTP server running in background across multiple test cases. For this, there are *module* or *session* [scopes](https://docs.pytest.org/en/6.2.x/fixture.html#scope-sharing-fixtures-across-classes-modules-packages-or-session) which have a lifetime beyond the default *function* scope of just a single test.