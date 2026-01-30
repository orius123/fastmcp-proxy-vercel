"""
FastMCP Proxy with Descope Authentication.

This proxy sits between MCP clients and target MCP servers, handling:
- OAuth authentication via Descope
- Automatic proxy mounting to forward requests to target MCP servers at startup
"""

import logging
import os
from contextlib import asynccontextmanager

from fastmcp import FastMCP
from fastmcp.client.transports import StreamableHttpTransport
from fastmcp.server.auth.providers.descope import DescopeProvider

logger = logging.getLogger(__name__)

# Configuration from environment
DESCOPE_CONFIG_URL = os.environ.get("DESCOPE_CONFIG_URL", "")
TARGET_MCP_SERVER_URL = os.environ.get("TARGET_MCP_SERVER_URL", "")
TARGET_TOKEN = os.environ.get("TARGET_TOKEN", "")

# Auto-detect SERVER_URL: prefer explicit, then Vercel URL, then localhost fallback
SERVER_URL = os.environ.get("SERVER_URL") or (
    f"https://{os.environ['VERCEL_URL']}"
    if os.environ.get("VERCEL_URL")
    else "http://localhost:8000"
)


@asynccontextmanager
async def lifespan(server: FastMCP):
    """Mount target MCP server at startup."""
    if TARGET_MCP_SERVER_URL:
        try:
            headers = {}
            if TARGET_TOKEN:
                headers["Authorization"] = f"Bearer {TARGET_TOKEN}"

            transport = StreamableHttpTransport(
                url=TARGET_MCP_SERVER_URL,
                headers=headers if headers else None,
            )

            proxy = FastMCP.as_proxy(transport)
            mcp.mount(proxy, prefix="target")
            logger.info(f"Mounted target server: {TARGET_MCP_SERVER_URL}")
        except Exception as e:
            logger.error(f"Failed to mount target server: {e}")
            raise
    else:
        logger.warning("TARGET_MCP_SERVER_URL not set - proxy running without target")

    yield {}


# Set up Descope auth provider if configured
auth_provider = None
if DESCOPE_CONFIG_URL:
    auth_provider = DescopeProvider(
        config_url=DESCOPE_CONFIG_URL,
        base_url=SERVER_URL,
    )

mcp = FastMCP(
    "Descope MCP Proxy",
    instructions="A security-first MCP proxy with Descope-based agentic authorization. "
    "All target server tools are available with the 'target_' prefix.",
    lifespan=lifespan,
    auth=auth_provider,
)

app = mcp.http_app(transport="http")
