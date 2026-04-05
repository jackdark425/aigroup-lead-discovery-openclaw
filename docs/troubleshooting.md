# Troubleshooting

Use this page if the plugin installs but your first run does not behave as expected.

## Healthy Install Checklist

Run:

```bash
openclaw plugins inspect aigroup-lead-discovery-openclaw
openclaw skills list
```

Healthy results usually look like this:

- plugin status shows `loaded`
- plugin id shows `aigroup-lead-discovery-openclaw`
- skills such as `client-initial-screening` and `company-event-scan` appear as `ready`

## Healthy First Result

A successful first run normally includes:

- a confirmed company identity
- a short company summary
- a banker-facing reason to contact
- risk flags
- next-step suggestions

If you use `client-initial-screening`, expect an answer shaped roughly like:

```text
Company summary
- [company identity and operating profile]

Reason to contact
- [why the account is worth a banker follow-up]

Risk flags
- [main public risk signals or missing-data caveats]

Next steps
- [three concrete banker actions]
```

## If The Plugin Installed But Skills Do Not Appear

Check:

- the plugin was installed under the correct id
- OpenClaw gateway was restarted after install
- your OpenClaw config does not block the plugin via `plugins.allow`

Recommended trust pinning:

```json
{
  "plugins": {
    "allow": [
      "aigroup-lead-discovery-openclaw",
      "aigroup-financial-services-openclaw"
    ]
  }
}
```

## If PrimeMatrixData Or Tianyancha Do Not Return Data

This plugin expects the corresponding credentials to exist in your OpenClaw config or environment.

Check for:

- `PRIMEMATRIX_MCP_API_KEY`
- `PRIMEMATRIX_BASE_URL`
- `TIANYANCHA_MCP_URL`
- `TIANYANCHA_AUTHORIZATION`

The bundled Python bridges also try to read these values from your OpenClaw profile config, including profile-style directories such as `~/.openclaw-profile-name/openclaw.json`.

## If You See A Trust Warning

`plugins.allow is empty` is a host warning, not a plugin failure.

Pin the two AIGroup suite ids in your OpenClaw config, then restart the gateway.

## If Terminal Invocation Fails

Start with a simple call:

```bash
openclaw agent --agent main --session-id banker-demo-101 -m "Use the client-initial-screening skill for 华为技术有限公司. Return company summary, reason_to_contact, risk_flags, and next_steps."
```

If your environment uses a different default agent, replace `main` with your agent id.

## Recommended Escalation Order

1. Confirm plugin install and `loaded` status.
2. Confirm skills show as `ready`.
3. Confirm credentials exist for PrimeMatrixData and Tianyancha.
4. Retry with the copy-paste example prompt from [Example Prompts](./example-prompts.md).
5. If needed, reinstall the plugin from Hub and retry.
