"""Minimal MCP server for the NZBN (New Zealand Business Number) API."""

import os
import json
from typing import Optional

import httpx
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, ConfigDict

# Constants
NZBN_API_BASE_URL = os.getenv("NZBN_API_BASE_URL", "https://api.business.govt.nz/gateway/nzbn/v5")
NZBN_API_KEY = os.getenv("NZBN_API_KEY", "")

mcp = FastMCP("nzbn_mcp")


class GetEntityInput(BaseModel):
    """Input model for get_entity tool."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    nzbn: str = Field(
        ...,
        description="The 13-digit New Zealand Business Number (e.g., '9429041864373')",
        min_length=13,
        max_length=13,
        pattern=r"^\d{13}$",
    )


def _get_headers() -> dict[str, str]:
    """Return headers for NZBN API requests."""
    return {
        "Ocp-Apim-Subscription-Key": NZBN_API_KEY,
        "Accept": "application/json",
    }


def _handle_api_error(e: Exception) -> str:
    """Format API errors into actionable messages."""
    if isinstance(e, httpx.HTTPStatusError):
        status = e.response.status_code
        if status == 404:
            return "Error: Entity not found. Verify the NZBN is correct."
        if status == 401:
            return "Error: Unauthorised. Check your NZBN_API_KEY environment variable."
        if status == 403:
            return "Error: Forbidden. Your subscription may not have access to this resource."
        if status == 429:
            return "Error: Rate limit exceeded. Wait before retrying."
        return f"Error: API returned status {status}."
    if isinstance(e, httpx.TimeoutException):
        return "Error: Request timed out. Try again."
    return f"Error: {type(e).__name__}: {e}"


@mcp.tool(
    name="get_entity",
    annotations={
        "title": "Get NZBN Entity",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def get_entity(params: GetEntityInput) -> str:
    """Retrieve full details for a New Zealand business by its NZBN.

    Returns the entity's primary business data including legal name, trading names,
    entity type, status, addresses, directors, shareholders, and other registration details.

    Args:
        params: GetEntityInput containing the 13-digit NZBN.

    Returns:
        JSON string with the entity's full business data from the NZBN Register.
    """
    url = f"{NZBN_API_BASE_URL}/entities/{params.nzbn}"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=_get_headers())
            response.raise_for_status()
            return json.dumps(response.json(), indent=2)
    except Exception as e:
        return _handle_api_error(e)


if __name__ == "__main__":
    mcp.run()
