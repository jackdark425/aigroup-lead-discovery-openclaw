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
const BASE_URL = (
  OPENCLAW_ENV.PRIMEMATRIX_BASE_URL ||
  "https://mcp.yidian.cn/api"
).replace(/\/+$/, "");
const MCP_API_KEY =
  OPENCLAW_ENV.PRIMEMATRIX_MCP_API_KEY ||
  "";

const TOOLS = [
  {
    name: "company_name",
    description: "获取企业工商信息。先根据模糊公司名匹配精确公司名列表；在调用其他依赖公司名称的工具前应先调用此工具。",
    inputSchema: {
      type: "object",
      properties: {
        blur_name: {
          type: "string",
          description: "企业相关关键字，输入字数>=2且不能仅输入“公司”或“有限公司”",
        },
      },
      required: ["blur_name"],
      additionalProperties: false,
    },
  },
  {
    name: "basic_info",
    description: "获取企业工商信息，包括企业状态、法人、统一信用代码、成立日期、注册资金、行业、地址、经营范围等。",
    inputSchema: {
      type: "object",
      properties: { company_name: { type: "string", description: "公司精确名称" } },
      required: ["company_name"],
      additionalProperties: false,
    },
  },
  {
    name: "judicial_info",
    description: "获取企业司法信息，包括立案、法院公告、开庭公告、执行信息、司法拍卖、破产信息等。",
    inputSchema: {
      type: "object",
      properties: { company_name: { type: "string", description: "公司精确名称" } },
      required: ["company_name"],
      additionalProperties: false,
    },
  },
  {
    name: "risk_info",
    description: "获取企业风险信息，包括经营异常、失信被执行人、严重违法、重大税收违法、限制高消费等。",
    inputSchema: {
      type: "object",
      properties: { company_name: { type: "string", description: "公司精确名称" } },
      required: ["company_name"],
      additionalProperties: false,
    },
  },
  {
    name: "ip_info",
    description: "获取企业知识产权信息，包括专利和商标信息。",
    inputSchema: {
      type: "object",
      properties: { company_name: { type: "string", description: "公司精确名称" } },
      required: ["company_name"],
      additionalProperties: false,
    },
  },
  {
    name: "shareholder_info",
    description: "获取企业股东信息，包括十大流通股及工商登记股东信息。",
    inputSchema: {
      type: "object",
      properties: { company_name: { type: "string", description: "公司精确名称" } },
      required: ["company_name"],
      additionalProperties: false,
    },
  },
  {
    name: "honor_info",
    description: "获取企业荣誉信息，包括地区、荣誉名称、级别、发布单位、发布日期等。",
    inputSchema: {
      type: "object",
      properties: { company_name: { type: "string", description: "公司精确名称" } },
      required: ["company_name"],
      additionalProperties: false,
    },
  },
  {
    name: "statistic_info",
    description: "按条件查询企业信息。",
    inputSchema: {
      type: "object",
      properties: {
        industry: { type: "string", description: "公司所属行业，为2017年国标行业分类" },
        entstatus: { type: "string", description: "公司状态，默认输入存续" },
        start_date: { type: "string", description: "成立时间自，格式 YYYY-MM-DD" },
        end_date: { type: "string", description: "成立时间至，格式 YYYY-MM-DD" },
        district_code: { type: "string", description: "企业所属区域编码，如 110000" },
        page: { type: "number", description: "查询页数，默认 1" },
      },
      required: ["industry", "entstatus", "start_date", "end_date", "district_code", "page"],
      additionalProperties: false,
    },
  },
  {
    name: "stk_company_basic_info",
    description: "获取企业上市信息与债券信息，包括股票代码、股票简称、上市交易所、债券信息等。",
    inputSchema: {
      type: "object",
      properties: { company_name: { type: "string", description: "公司精确名称" } },
      required: ["company_name"],
      additionalProperties: false,
    },
  },
  {
    name: "job_info",
    description: "获取企业招聘信息，包括招聘时间、薪资、教育要求、岗位描述等。",
    inputSchema: {
      type: "object",
      properties: { company_name: { type: "string", description: "公司精确名称" } },
      required: ["company_name"],
      additionalProperties: false,
    },
  },
  {
    name: "finance_info",
    description: "获取企业财务信息，包括资产负债表、利润表和现金流量表。若用户未提及时间，默认 2020-2024。",
    inputSchema: {
      type: "object",
      properties: {
        company_name: { type: "string", description: "公司精确名称" },
        start_year: { type: "string", description: "查询年份自" },
        end_year: { type: "string", description: "查询年份至" },
      },
      required: ["company_name", "start_year", "end_year"],
      additionalProperties: false,
    },
  },
];

const ENDPOINTS = {
  company_name: ["/company_name", { blur_name: "blur_name" }],
  basic_info: ["/basic_info", { company_name: "company" }],
  judicial_info: ["/judicial_info", { company_name: "company" }],
  risk_info: ["/risk_info", { company_name: "company" }],
  ip_info: ["/ip_info", { company_name: "company" }],
  shareholder_info: ["/shareholder_info", { company_name: "company" }],
  honor_info: ["/honor_info", { company_name: "company" }],
  statistic_info: [
    "/statistic_info",
    {
      industry: "industro",
      entstatus: "entstatus",
      start_date: "start_date",
      end_date: "end_date",
      district_code: "district_code",
      page: "page",
    },
  ],
  stk_company_basic_info: ["/stk_company_basic_info", { company_name: "company" }],
  job_info: ["/job_info", { company_name: "company" }],
  finance_info: [
    "/finance_info",
    { company_name: "company", start_year: "start_year", end_year: "end_year" },
  ],
};

let readBuffer = Buffer.alloc(0);

function log(message) {
  void message;
}

function writeMessage(message) {
  const payload = Buffer.from(JSON.stringify(message), "utf8");
  log(`OUT ${payload.toString("utf8")}`);
  process.stdout.write(`Content-Length: ${payload.length}\r\n\r\n`);
  process.stdout.write(payload);
}

function makeTextResult(text, isError = false) {
  const result = { content: [{ type: "text", text }] };
  if (isError) result.isError = true;
  return result;
}

function sendResponse(id, result) {
  writeMessage({ jsonrpc: "2.0", id, result });
}

function sendError(id, message) {
  writeMessage({ jsonrpc: "2.0", id, error: { code: -32000, message } });
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

async function requestJson(pathname, argMap, args) {
  const query = new URLSearchParams();
  for (const [inputKey, remoteKey] of Object.entries(argMap)) {
    if (args[inputKey] !== undefined && args[inputKey] !== null) {
      query.set(remoteKey, String(args[inputKey]));
    }
  }
  const url = new URL(`${BASE_URL}${pathname}`);
  url.search = query.toString();
  const response = await fetch(url, {
    headers: {
      Accept: "application/json",
      ...(MCP_API_KEY ? { "X-API-Key": MCP_API_KEY } : {}),
    },
  });
  const text = await response.text();
  if (!response.ok) {
    throw new Error(`PrimeMatrix request failed (${response.status}): ${text.slice(0, 400)}`);
  }
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

async function callTool(toolName, toolArgs = {}) {
  if (!ENDPOINTS[toolName]) {
    throw new Error(`Unknown tool: ${toolName}`);
  }
  const [pathname, argMap] = ENDPOINTS[toolName];
  return requestJson(pathname, argMap, toolArgs);
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
      serverInfo: { name: "prime-matrix-codex-bridge", version: "1.1.0" },
    });
    return;
  }
  if (method === "notifications/initialized") return;
  if (method === "resources/list") {
    sendResponse(id, { resources: [] });
    return;
  }
  if (method === "resources/templates/list") {
    sendResponse(id, { resourceTemplates: [] });
    return;
  }
  if (method === "tools/list") {
    sendResponse(id, { tools: TOOLS });
    return;
  }
  if (method === "tools/call") {
    const toolName = message.params?.name;
    const toolArgs = message.params?.arguments || {};
    try {
      const data = await callTool(toolName, toolArgs);
      sendResponse(id, makeTextResult(JSON.stringify(data, null, 2)));
    } catch (error) {
      sendResponse(id, makeTextResult(String(error), true));
    }
    return;
  }
  if (id !== undefined) sendError(id, `Unsupported method: ${method}`);
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
        sendError(message.id, `PrimeMatrix bridge error: ${error instanceof Error ? error.message : String(error)}`);
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
