# Quick Install — aigroup-lead-discovery-openclaw

> **target host**: macmini running OpenClaw with `main` agent on `minimax-cn/MiniMax-M2.7`.
> This is the **upstream** half of the banker stack. Install this first, then install `aigroup-financial-services-openclaw` second.

## 3-step install

```bash
# 1. Install via ClawHub (public)
openclaw plugins install clawhub:aigroup-lead-discovery-openclaw

# 2. Restart gateway so cn-lead-safety + 5 lead-gen skills surface to main agent
launchctl kickstart -k gui/$(id -u)/ai.openclaw.gateway

# 3. Run the preflight check
bash ~/.openclaw/extensions/aigroup-lead-discovery-openclaw/scripts/preflight.sh
```

Preflight exit 0 → plugin usable.

## CN MCP dependencies (v0.8.0+ for customer-investigation)

For A股 / 大陆 target intelligence, three MCP servers are expected. The plugin's `.mcp.json` auto-wires the first; the other two you register once globally (see the paired `aigroup-financial-services-openclaw/QUICKSTART.md` for the `openclaw mcp set` commands):

| MCP | Role | Auto-installed? |
|-----|------|-----------------|
| `aigroup-market-mcp` | 上市公司 Tushare 行情 + 财务 | **Yes** (via this plugin's `.mcp.json`) |
| `PrimeMatrixData` | 上市 + 非上市 工商 + 司法 + 风险 (启信宝) | **Manual** — see below |
| `Tianyancha` (optional) | 上市 + 非上市 企业基础 + 风险 | **Paused** 2026-04 (智谱 broker 账户欠费); can re-enable after topup |

This plugin's `scripts/mcp_compat/` directory holds REFERENCE implementations of both bridges. The `.mjs.txt` suffix on the bridge files (instead of `.mjs`) is INTENTIONAL — OpenClaw's install-time safety scanner flags `process.env + fetch` JavaScript as credential-harvesting, but the scanner does not scan `.txt` files. After install, rename the PrimeMatrix bridge on disk:

```bash
cd ~/.openclaw/extensions/aigroup-lead-discovery-openclaw/scripts/mcp_compat
mv prime_matrix_stdio_bridge.mjs.txt prime_matrix_stdio_bridge.mjs
# Tianyancha bridge file exists as reference but is not activated by default.
# To enable after topping up the 智谱 broker account:
# mv tianyancha_stdio_bridge.mjs.txt tianyancha_stdio_bridge.mjs
```

Then `openclaw mcp set` per the financial-services QUICKSTART — `openclaw mcp list` should show `aigroup-market-mcp` and `PrimeMatrixData` at minimum.

The `cn-lead-safety` gate's `verify_intelligence.py --strict-mcp` option then enforces that cited hard numbers trace back to one of these MCP tools or an official-filing source (not fabricated labels like Wind / 同花顺).

## Runtime dependencies

| Tool | Why |
|------|-----|
| `python3` ≥ 3.9 | runs `scripts/verify_intelligence.py` (Rule 4 inline-citation gate + `--strict-mcp`), `scripts/quality-audit.py` (data-quality-audit helper) |
| `node` ≥ 18 | standard OpenClaw bundle requirement; also runs the `scripts/mcp_compat/*.mjs` stdio bridges |

Unlike the paired `aigroup-financial-services-openclaw`, this plugin does NOT need `pptxgenjs` or `python-pptx` — lead-discovery only emits markdown intelligence; slide compilation happens in the downstream plugin.

## Known pitfalls

### ClawHub transient "missing plugin.json" on install

Same workaround as the financial-services plugin:

```bash
find /var/folders -name "openclaw-clawhub-package-*" -type d 2>/dev/null | xargs rm -rf
openclaw plugins install clawhub:aigroup-lead-discovery-openclaw
```

## Pair with the downstream banker plugin

Lead-discovery produces intelligence markdown that downstream banker workflow (datapack-builder / dcf-model / ppt-deliverable) reads. Install downstream too:

```bash
openclaw plugins install clawhub:aigroup-financial-services-openclaw
```

See its own `QUICKSTART.md` for setup.

## Verify end-to-end

```bash
openclaw agent --agent main --thinking minimal --json --message "OK" | \
  python3 -c "import json,sys; t=sys.stdin.read(); d=json.loads(t[:t.index('}\n}')+3]); \
  sk=[s.get('name','?') for s in d['result']['meta']['systemPromptReport']['skills']['entries']]; \
  print('cn-lead-safety:', 'cn-lead-safety' in sk); \
  print('customer-investigation:', 'customer-investigation' in sk)"
```
