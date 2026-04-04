#!/usr/bin/env node

import fs from "node:fs";
import os from "node:os";
import path from "node:path";

function loadOpenClawEnv() {
  try {
    const cfg = JSON.parse(
      fs.readFileSync(path.join(os.homedir(), ".openclaw", "openclaw.json"), "utf8"),
    );
    return cfg?.env || {};
  } catch {
    return {};
  }
}

const OPENCLAW_ENV = loadOpenClawEnv();
const REMOTE_URL = OPENCLAW_ENV.TIANYANCHA_MCP_URL;
const AUTHORIZATION = OPENCLAW_ENV.TIANYANCHA_AUTHORIZATION;

let sessionId = null;
let readBuffer = Buffer.alloc(0);

const TOOLS = [
  {
    name: "companyBaseInfo",
    description: "查询企业工商登记与基础信息，用于确认企业主体、法人、注册资本、成立时间与经营状态。",
    inputSchema: {
      type: "object",
      properties: {
        companyName: {
          type: "string",
          description: "企业精确名称",
        },
      },
      required: ["companyName"],
      additionalProperties: true,
    },
  },
  {
    name: "risk",
    description: "查询企业法律、经营与风险信号，用于客户准入前的风险筛查。",
    inputSchema: {
      type: "object",
      properties: {
        companyName: {
          type: "string",
          description: "企业精确名称",
        },
      },
      required: ["companyName"],
      additionalProperties: true,
    },
  },
];

function log(message) {
  void message;
}

function writeMessage(message) {
  const payload = Buffer.from(JSON.stringify(message), "utf8");
  log(`OUT ${payload.toString("utf8")}`);
  process.stdout.write(`Content-Length: ${payload.length}\r\n\r\n`);
  process.stdout.write(payload);
}

function sendError(id, message) {
  writeMessage({ jsonrpc: "2.0", id, error: { code: -32000, message } });
}

function sendResponse(id, result) {
  writeMessage({ jsonrpc: "2.0", id, result });
}

function tryParseMessage() {
  const delimiter = readBuffer.indexOf("\r\n\r\n");
  if (delimiter === -1) return null;
  const headerText = readBuffer.subarray(0, delimiter).toString("utf8");
  const headers = Object.fromEntries(
    headerText
      .split("\r\n")
      .map((line) => line.split(/:\s*/, 2))
      .filter(([key, value]) => key && value),
  );
  const length = Number.parseInt(headers["Content-Length"] || headers["content-length"] || "0", 10);
  if (!Number.isFinite(length) || length <= 0) {
    readBuffer = readBuffer.subarray(delimiter + 4);
    return null;
  }
  const bodyStart = delimiter + 4;
  const bodyEnd = bodyStart + length;
  if (readBuffer.length < bodyEnd) return null;
  const body = readBuffer.subarray(bodyStart, bodyEnd).toString("utf8");
  readBuffer = readBuffer.subarray(bodyEnd);
  log(`IN ${body}`);
  return JSON.parse(body);
}

function parseSseBody(body) {
  const chunks = [];
  for (const block of body.split("\n\n")) {
    for (const line of block.split(/\r?\n/)) {
      if (line.startsWith("data:")) chunks.push(line.slice(5).trim());
    }
  }
  if (!chunks.length) return null;
  return JSON.parse(chunks.join(""));
}

async function remotePost(payload, allowMissingSession = false) {
  if (!REMOTE_URL || !AUTHORIZATION) {
    throw new Error("Tianyancha environment is not configured");
  }
  const headers = {
    Authorization: AUTHORIZATION,
    "Content-Type": "application/json",
    Accept: "application/json, text/event-stream",
  };
  if (sessionId) headers["mcp-session-id"] = sessionId;
  const response = await fetch(REMOTE_URL, {
    method: "POST",
    headers,
    body: JSON.stringify(payload),
  });
  const nextSessionId = response.headers.get("mcp-session-id");
  if (nextSessionId) sessionId = nextSessionId;
  const text = await response.text();
  if (!response.ok && !(allowMissingSession && response.status === 400)) {
    throw new Error(`Tianyancha request failed (${response.status}): ${text.slice(0, 400)}`);
  }
  const contentType = response.headers.get("content-type") || "";
  if (!text.trim()) return null;
  if (contentType.includes("text/event-stream")) return parseSseBody(text);
  return JSON.parse(text);
}

function normalizeToolArgs(toolName, toolArgs = {}) {
  if ((toolName === "companyBaseInfo" || toolName === "risk") && toolArgs.companyName && !toolArgs.keyword) {
    return { ...toolArgs, keyword: toolArgs.companyName };
  }
  return toolArgs;
}

async function callTool(toolName, toolArgs = {}) {
  const response = await remotePost(
    {
      jsonrpc: "2.0",
      id: "cli-call",
      method: "tools/call",
      params: { name: toolName, arguments: normalizeToolArgs(toolName, toolArgs) },
    },
    true,
  );
  if (response?.error) {
    throw new Error(response.error.message || JSON.stringify(response.error));
  }
  const text = response?.result?.content?.map((item) => item?.text || "").join("\n").trim();
  if (!text) return response?.result ?? response ?? {};
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

async function handleMessage(message) {
  const { id, method } = message;
  if (method === "initialize") {
    sendResponse(id, {
      protocolVersion: message.params?.protocolVersion || "2025-03-26",
      capabilities: {
        tools: { listChanged: false },
        resources: { listChanged: false },
      },
      serverInfo: { name: "tianyancha-codex-bridge", version: "1.1.0" },
    });
    return;
  }
  if (method === "notifications/initialized") {
    try {
      await remotePost({ jsonrpc: "2.0", method: "notifications/initialized", params: {} }, true);
    } catch {
      // no-op
    }
    return;
  }
  if (method === "tools/list") {
    sendResponse(id, { tools: TOOLS });
    return;
  }
  if (method === "resources/list") {
    sendResponse(id, { resources: [] });
    return;
  }
  if (method === "resources/templates/list") {
    sendResponse(id, { resourceTemplates: [] });
    return;
  }
  const response = await remotePost(message, true);
  if (response) {
    writeMessage(response);
  } else if (id !== undefined) {
    sendResponse(id, {});
  }
}

async function runCli() {
  const [, , toolName, rawArgs = "{}"] = process.argv;
  if (!toolName) return false;
  try {
    const parsedArgs = JSON.parse(rawArgs);
    const data = await callTool(toolName, parsedArgs);
    process.stdout.write(`${JSON.stringify(data, null, 2)}\n`);
    return true;
  } catch (error) {
    process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`);
    process.exit(1);
  }
}

if (await runCli()) {
  process.exit(0);
}

process.stdin.on("data", async (chunk) => {
  readBuffer = Buffer.concat([readBuffer, chunk]);
  while (true) {
    const message = tryParseMessage();
    if (!message) break;
    try {
      await handleMessage(message);
    } catch (error) {
      if (message.id !== undefined) {
        sendError(message.id, `Tianyancha bridge error: ${error instanceof Error ? error.message : String(error)}`);
      }
    }
  }
});

process.stdin.on("end", () => process.exit(0));
process.on("uncaughtException", (error) => {
  log(`UNCAUGHT ${error?.stack || error}`);
  process.exit(1);
});
process.on("unhandledRejection", (error) => {
  log(`UNHANDLED ${error?.stack || error}`);
  process.exit(1);
});
