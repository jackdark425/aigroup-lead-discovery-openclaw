# aigroup-lead-discovery-openclaw

Lead-discovery and company-intelligence suite for banker workflows on OpenClaw.

This plugin is the recommended first install in the AIGroup banker stack. Install it first as the intelligence and data-entry suite, then add `aigroup-financial-services-openclaw` as the downstream modeling and deliverables suite.

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
.mcp.optional.json
skills/
scripts/mcp_compat/
```

OpenClaw detects this repository as a Claude bundle and maps:

- `skills/` into normal OpenClaw skills
- `.mcp.optional.json` as an optional MCP template

## Install

Recommended suite-first install flow:

```bash
openclaw plugins install aigroup-lead-discovery-openclaw
openclaw plugins install aigroup-financial-services-openclaw
```

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

- `aigroup-lead-discovery-openclaw@0.1.6`

Recommended companion package:

- `aigroup-financial-services-openclaw`

Quick install guide:

- [docs/quickstart.md](docs/quickstart.md)

## Verify After Install

```bash
openclaw plugins inspect aigroup-lead-discovery-openclaw
openclaw plugins inspect aigroup-financial-services-openclaw
openclaw skills list
```

## Release Prep

Validate the repository bundle shape directly:

```bash
python3 scripts/validate_bundle.py .
```

ClawHub releases should be published from the repository root. `.clawhubignore` trims non-runtime files while preserving `.claude-plugin/plugin.json`, which is required for correct install identity on fresh OpenClaw profiles.

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
- The Tianyancha and PrimeMatrixData integrations are routed through bundled Python bridge scripts. The default suite path uses skills plus stable `exec` commands; the optional MCP template is kept for advanced experiments only.
- The recommended deployment model is suite-first: use this plugin for intelligence and data gathering, then use `aigroup-financial-services-openclaw` for modeling and deliverable workflows.
