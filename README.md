# FastMCP Descope Proxy

Add [Descope](https://www.descope.com) authentication to any MCP server without modifying its code.

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Forius123%2Ffastmcp-proxy-vercel&env=DESCOPE_CONFIG_URL,TARGET_MCP_SERVER_URL&envDescription=Configure%20your%20Descope%20and%20target%20MCP%20server&envLink=https%3A%2F%2Fgithub.com%2Forius123%2Ffastmcp-proxy-vercel%23configuration)

## Use Case

You have an MCP server running somewhere (your own infrastructure, cloud function, etc.) and want to add OAuth authentication via Descope's Agentic Identity Hub—without changing your server code.

Deploy this proxy, point it at your MCP server, and clients authenticate through Descope before reaching your server.

## Architecture

```
┌─────────────┐     ┌─────────────────┐     ┌─────────┐     ┌────────────────┐
│             │     │                 │     │         │     │                │
│  MCP Client │────▶│  This Proxy     │────▶│ Descope │     │  Your MCP      │
│  (Claude)   │     │  (Vercel)       │     │  Auth   │     │  Server        │
│             │◀────│                 │◀────│         │     │                │
└─────────────┘     └────────┬────────┘     └─────────┘     └────────────────┘
                             │                                      ▲
                             │      (after authentication)          │
                             └──────────────────────────────────────┘
```

## Quick Start

### 1. Deploy to Vercel

Click the "Deploy with Vercel" button above and configure:

| Variable | Value |
|----------|-------|
| `DESCOPE_CONFIG_URL` | Your Descope MCP Server well-known URL |
| `TARGET_MCP_SERVER_URL` | URL of your existing MCP server |

### 2. Configure Descope

1. Go to [Descope Console](https://app.descope.com) → MCP Servers
2. Create a new MCP Server with DCR enabled
3. Set the Resource URL to your Vercel deployment URL
4. Copy the Well-Known URL for `DESCOPE_CONFIG_URL`

### 3. Connect Your Client

Point your MCP client (Claude Desktop, Cursor, etc.) to your Vercel deployment URL. The proxy handles OAuth automatically.

## Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `DESCOPE_CONFIG_URL` | Yes | Your Descope MCP Server well-known URL |
| `TARGET_MCP_SERVER_URL` | Yes | URL of your MCP server to proxy |
| `TARGET_TOKEN` | No | Bearer token if your target server requires auth |
| `SERVER_URL` | No | Auto-detected on Vercel |

## How It Works

1. Client connects to the proxy
2. Proxy redirects to Descope for OAuth authentication
3. After auth, proxy forwards all requests to your target MCP server
4. Target server tools are exposed with a `target_` prefix

Example: If your server has a `get_weather` tool, clients see `target_get_weather`.

## Local Development

### Testing the Proxy

A sample `target_server.py` is included for local testing only:

```bash
# Terminal 1: Run mock target server (for testing only)
TARGET_API_TOKEN="test-secret" uv run fastmcp run target_server.py --transport http --port 9000

# Terminal 2: Run proxy
DESCOPE_CONFIG_URL="your-url" \
TARGET_MCP_SERVER_URL="http://localhost:9000/mcp" \
TARGET_TOKEN="test-secret" \
uv run fastmcp run api/index.py --transport http --port 8000
```

In production, `TARGET_MCP_SERVER_URL` points to your real MCP server.

### Running Without Vercel

```bash
pip install -r requirements.txt
fastmcp run api/index.py --transport http --port 8000
```

## License

MIT
