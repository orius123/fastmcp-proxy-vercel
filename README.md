# FastMCP Descope Proxy

A security-first MCP proxy that authenticates users via [Descope](https://www.descope.com) and forwards requests to target MCP servers.

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2FYOUR_ORG%2Ffastmcp-descope-proxy&env=DESCOPE_CONFIG_URL,TARGET_MCP_SERVER_URL,TARGET_TOKEN&envDescription=Configure%20your%20Descope%20and%20target%20MCP%20server&envLink=https%3A%2F%2Fgithub.com%2FYOUR_ORG%2Ffastmcp-descope-proxy%23configuration)

## Architecture

```
┌─────────────┐     ┌─────────────────┐     ┌─────────┐     ┌────────────────┐
│             │     │                 │     │         │     │                │
│  MCP Client │────▶│  This Proxy     │────▶│ Descope │     │  Target MCP    │
│  (Claude)   │     │                 │     │  Auth   │     │  Server        │
│             │◀────│                 │◀────│         │     │                │
└─────────────┘     └────────┬────────┘     └─────────┘     └────────────────┘
                             │                                      ▲
                             │      (after authentication)          │
                             └──────────────────────────────────────┘
```

## Features

- OAuth 2.1 authentication via Descope's Agentic Identity Hub
- Automatic proxy mounting to target MCP servers at startup
- Protected Resource Metadata (RFC 9728) endpoint
- Works with any MCP-compatible client (Claude Desktop, Cursor, etc.)

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
# or
uv pip install -r requirements.txt
```

### 2. Configure Descope

1. Go to [Descope Console](https://app.descope.com) → MCP Servers
2. Create a new MCP Server with DCR enabled
3. Copy your Well-Known URL

### 3. Set Environment Variables

```bash
cp .env.example .env
# Edit .env with your values
```

### 4. Run the Proxy

```bash
# Using fastmcp CLI
fastmcp run api/index.py --transport http --port 8000

# Or with uv
uv run fastmcp run api/index.py --transport http --port 8000
```

### 5. Test

```bash
# Check the OAuth metadata endpoint
curl http://localhost:8000/.well-known/oauth-protected-resource/mcp
```

## Configuration

| Variable | Description |
|----------|-------------|
| `DESCOPE_CONFIG_URL` | Your Descope MCP Server well-known URL |
| `SERVER_URL` | Public URL of this proxy (auto-detected on Vercel) |
| `TARGET_MCP_SERVER_URL` | URL of the target MCP server to proxy |
| `TARGET_TOKEN` | Optional Bearer token for target server auth |

## How It Works

Once deployed, the proxy:

1. Authenticates incoming MCP clients via Descope OAuth
2. Mounts the target MCP server at startup
3. Exposes all target server tools with a `target_` prefix

For example, if your target server has a `get_weather` tool, it becomes `target_get_weather` through the proxy.

## Deployment

### Vercel (One-Click)

Click the "Deploy with Vercel" button above, or:

```bash
vercel
```

The proxy auto-detects its URL on Vercel via `VERCEL_URL` environment variable.

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["fastmcp", "run", "api/index.py", "--transport", "http", "--port", "8000"]
```

## Development

### Testing with a Local Target Server

The `target_server.py` file provides a simple authenticated MCP server for testing:

```bash
# Terminal 1: Run target server
TARGET_API_TOKEN="test-secret" uv run fastmcp run target_server.py --transport http --port 9000

# Terminal 2: Run proxy
DESCOPE_CONFIG_URL="your-url" TARGET_MCP_SERVER_URL="http://localhost:9000/mcp" TARGET_TOKEN="test-secret" uv run fastmcp run api/index.py --transport http --port 8000
```

## License

MIT
