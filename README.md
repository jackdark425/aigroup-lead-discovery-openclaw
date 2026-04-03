# aigroup-lead-discovery-openclaw

Lead-discovery and company-watch plugin for banker outbound workflows on OpenClaw.

This plugin is the recommended AIGroup data-entry layer for banker outbound, customer research, and external lead intelligence workflows.

This repository is a standalone OpenClaw-compatible Claude bundle. It packages:

- four banker SOP skills for lead discovery
- two enterprise-intelligence MCP connectors
- local stdio bridge scripts so the plugin does not depend on a developer-specific machine path

It is also designed to be used alongside the AIGroup data-service MCP stack:

- `aigroup-fmp-mcp`
- `aigroup-market-mcp`
- `aigroup-finnhub-mcp`
- `Tianyancha`
- `PrimeMatrixData`

## Included

### Skills

- `client-initial-screening`
- `company-event-scan`
- `key-account-briefing`
- `weekly-lead-watchlist`

### MCP connectors

- `PrimeMatrixData-stdio`
- `Tianyancha`

### Recommended companion AIGroup data services

- `aigroup-fmp-mcp`
- `aigroup-market-mcp`
- `aigroup-finnhub-mcp`

## Plugin Layout

```text
.claude-plugin/plugin.json
.mcp.json
skills/
scripts/mcp_compat/
```

OpenClaw detects this repository as a Claude bundle and maps:

- `skills/` into normal OpenClaw skills
- `.mcp.json` into bundle MCP settings

## Install

### OpenClaw Hub

```bash
openclaw plugins install aigroup-lead-discovery-openclaw
```

### Local path

```bash
openclaw plugins install ./aigroup-lead-discovery-openclaw
```

### GitHub shorthand

```bash
openclaw plugins install jackdark425/aigroup-lead-discovery-openclaw
```

Published package:

- `aigroup-lead-discovery-openclaw@0.1.1`

Recommended companion package:

- `aigroup-financial-services-openclaw`

Quick install guide:

- [docs/quickstart.md](docs/quickstart.md)

## Verify After Install

```bash
openclaw plugins inspect aigroup-lead-discovery-openclaw
openclaw skills list
```

## Release Prep

To prepare the minimal publishable artifact used for ClawHub releases:

```bash
python3 scripts/prepare_release_bundle.py /tmp/aigroup-lead-discovery-openclaw-release
```

To validate the repository bundle shape directly:

```bash
python3 scripts/validate_bundle.py .
```

## Environment

Set these before using the plugin:

- `PRIMEMATRIX_MCP_API_KEY`
- `PRIMEMATRIX_BASE_URL`
- `TIANYANCHA_MCP_URL`
- `TIANYANCHA_AUTHORIZATION`

## What Each Skill Does

### `client-initial-screening`

Quickly decide whether a company is worth contacting at all. Focuses on entity confirmation, operating status, growth clues, risk flags, and a recommended next action.

### `company-event-scan`

Turns web and enterprise-data signals into outreach triggers such as hiring, expansion, partnerships, honors, financing clues, and likely banking entry points.

### `key-account-briefing`

Produces a concise pre-meeting briefing for a banker before first contact or an on-site visit.

### `weekly-lead-watchlist`

Scans a batch list and ranks accounts into follow now, observe, or pause groups.

## Validation

This plugin has been validated on OpenClaw `2026.4.2` for:

- bundle loading
- MCP recognition
- skill discovery
- skill readiness

See [docs/validation.md](./docs/validation.md).

## Notes

- The plugin is distributed as a compatible bundle, not a native in-process OpenClaw plugin.
- The Tianyancha and PrimeMatrixData integrations are routed through local stdio bridges because that is the most reliable way to make them usable from bundle MCP today.
- The recommended deployment model is: use this plugin for intelligence and data gathering, then use `aigroup-financial-services-openclaw` for modeling and deliverable workflows.
