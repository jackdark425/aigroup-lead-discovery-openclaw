# Validation

## Scope

This plugin was validated as an OpenClaw-compatible Claude bundle.

## Verified

- `openclaw plugins inspect aigroup-lead-discovery-openclaw`
- bundle format detected as `claude`
- bundle MCP connectors recognized:
  - `PrimeMatrixData-stdio`
  - `Tianyancha`
- bundle skills discovered and marked `ready`:
  - `client-initial-screening`
  - `company-event-scan`
  - `key-account-briefing`
  - `weekly-lead-watchlist`

## Current shape

- Format: bundle
- Capability mode: non-capability
- Bundle capabilities: `skills`, `mcpServers`

## Notes

- This repository is intentionally kept as a standalone bundle root so it can be installed directly from a checked-out directory or GitHub source.
- MCP transport is implemented through stdio bridges to maximize compatibility with current OpenClaw bundle MCP handling.
