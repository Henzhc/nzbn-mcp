"""MCP server for the NZBN (New Zealand Business Number) API using FastMCP.from_openapi."""

import json
import os
from pathlib import Path

import httpx
from fastmcp import FastMCP

# Constants
NZBN_API_BASE_URL = os.getenv(
    "NZBN_API_BASE_URL", "https://api.business.govt.nz/gateway/nzbn/v5"
)
NZBN_API_KEY = os.getenv("NZBN_API_KEY", "")

# Load the OpenAPI spec from nzbn.json
spec_path = Path(__file__).parent.parent.parent / "nzbn.json"
with open(spec_path, "r", encoding="utf-8") as f:
    openapi_spec = json.load(f)

# Create an HTTP client configured for the NZBN API with authentication
client = httpx.AsyncClient(
    base_url=NZBN_API_BASE_URL,
    headers={
        "Ocp-Apim-Subscription-Key": NZBN_API_KEY,
        "Accept": "application/json",
    },
    timeout=30.0,
)

# Create the MCP server from the OpenAPI spec
mcp = FastMCP.from_openapi(
    openapi_spec=openapi_spec,
    client=client,
    name="NZBN MCP Server",
)

if __name__ == "__main__":
    mcp.run(transport="stdio")
