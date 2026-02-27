# AI Copilot Instructions for mcp-nzbn

## Project Overview
**mcp-nzbn** is a Model Context Protocol (MCP) server that provides Claude with access to the NZBN (New Zealand Business Number) API. It wraps the government-provided NZBN API to retrieve detailed business registration information through a single MCP tool.

## Architecture & Design

### Core Components
- **[nzbn_mcp.py](nzbn_mcp.py)**: The main MCP server implementation using FastMCP. Contains the entire server logic in a single file.
  - Defines the `get_entity` tool that queries the NZBN API for business details
  - Handles API authentication via `NZBN_API_KEY` environment variable
  - Implements comprehensive error handling with user-friendly messages
  - Uses async/await for non-blocking HTTP requests via `httpx`

- **[src/mcp_nzbn/](src/mcp_nzbn/)**: Package structure (currently minimal)
  - `__init__.py`: Entry point that delegates to `server.main()` (though `server` module doesn't exist yet)
  - Appears to be scaffolding for future expansion

### Data Flow
1. Claude sends a request with a 13-digit NZBN
2. `GetEntityInput` pydantic model validates the NZBN format (digits-only, exactly 13 chars)
3. `get_entity()` constructs the URL to `{NZBN_API_BASE_URL}/entities/{nzbn}`
4. Request includes `Ocp-Apim-Subscription-Key` header for API authentication
5. Response is parsed and returned as formatted JSON, or detailed error message if it fails

## Key Patterns & Conventions

### Error Handling
The `_handle_api_error()` function maps HTTP status codes to user-friendly messages:
- **404**: "Entity not found" - guides user to verify NZBN
- **401/403**: Authentication/authorization issues - suggests checking API credentials
- **429**: Rate limiting - advises retry
- **Timeouts**: Distinguishes network issues from server errors

This pattern should be applied to any new API interactions.

### Input Validation
Uses Pydantic's `BaseModel` with strict validation:
- `GetEntityInput` enforces exact 13-digit NZBN via regex pattern and min/max length
- `ConfigDict(extra="forbid")` rejects unknown fields
- `model_config` with `str_strip_whitespace=True` for robustness

### Tool Metadata
Tool annotations describe capabilities for Claude:
- `readOnlyHint: True` - doesn't modify data
- `destructiveHint: False` - safe to call
- `idempotentHint: True` - same input = same output
- `openWorldHint: True` - accesses external API

## Environment Configuration

### Required Variables
- `NZBN_API_KEY`: Subscription key for government NZBN API (critical)
- `NZBN_API_BASE_URL`: API endpoint (defaults to `https://api.business.govt.nz/gateway/nzbn/v5`)

When implementing new features requiring external APIs, follow this pattern of environment defaults.

## Common Tasks

### Adding New Tools
1. Create an input `BaseModel` in the main server file with strict validation
2. Use `@mcp.tool()` decorator with descriptive metadata
3. Implement async function that returns string (MCP requirement)
4. Handle errors with `_handle_api_error()` pattern or similar
5. Wrap complex data in `json.dumps()` for consistent output format

### Debugging
- Check `NZBN_API_KEY` is set correctly
- Verify NZBN format (13 digits, no special characters)
- Use httpx's timeout (default 30.0s) for slow networks
- Error messages indicate whether issue is configuration, rate limiting, or data validation

### Testing Integration
The project lacks explicit tests. When adding tests, use pytest with asyncio support, and mock httpx responses to avoid rate limiting.

## Dependencies
- **mcp**: FastMCP framework for building MCP servers
- **httpx**: Async HTTP client (chosen over requests for MCP async compatibility)
- **pydantic**: Input validation
- Core python 3.8+: asyncio, json, os, typing

Avoid adding synchronous HTTP libraries (requests) - stay async throughout.
