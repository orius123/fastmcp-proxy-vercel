"""
Example target MCP server for testing the proxy.

This simple server requires Bearer token authentication and provides
a few example tools to verify the proxy is working correctly.

Usage:
    TARGET_API_TOKEN="your-secret" uv run fastmcp run target_server.py --transport http --port 9000
"""

import os

from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_headers

REQUIRED_TOKEN = os.environ.get("TARGET_API_TOKEN", "test-secret-token")

mcp = FastMCP(
    "Example Target Server",
    instructions="A simple authenticated MCP server for testing.",
)


def _get_bearer_token() -> str | None:
    headers = get_http_headers()
    auth = headers.get("authorization", "") if headers else ""
    if auth.startswith("Bearer "):
        return auth[7:]
    return None


def _check_auth() -> dict | None:
    token = _get_bearer_token()
    if not token:
        return {"error": "Missing Authorization header", "code": "UNAUTHORIZED"}
    if token != REQUIRED_TOKEN:
        return {"error": "Invalid token", "code": "FORBIDDEN"}
    return None


@mcp.tool()
def whoami() -> dict:
    """Returns authentication status."""
    if err := _check_auth():
        return err
    token = _get_bearer_token()
    return {
        "authenticated": True,
        "token_preview": f"{token[:10]}..." if token and len(token) > 10 else token,
    }


@mcp.tool()
def get_secret() -> dict:
    """Returns a secret value (requires authentication)."""
    if err := _check_auth():
        return err
    return {
        "secret": "The answer to life, the universe, and everything is 42",
    }


@mcp.tool()
def echo(message: str) -> dict:
    """Echoes back the provided message (requires authentication)."""
    if err := _check_auth():
        return err
    return {"echo": message}


app = mcp.http_app(transport="http")
