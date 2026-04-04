---
name: client-initial-screening
description: 快速完成潜在客户初筛。适用于“先判断这家公司值不值得联系”“给我一个客户准入前的外网快筛”“帮我看这家企业有没有明显风险或营销切入点”。优先调用 PrimeMatrixData-stdio 与 Tianyancha，输出客户状态、增长信号、风险信号、建议动作。
---

# 新客户初筛

用于银行客户经理第一次判断一家企业是否值得进入跟进池。

## 目标

输出一份简洁、可执行的初筛结论，固定包含：

1. 企业身份是否明确
2. 企业是否正常经营
3. 是否存在明显风险信号
4. 是否存在增长、扩张、招聘、荣誉、知识产权等正面线索
5. 推荐下一步动作

## 工具顺序

1. `PrimeMatrixData-stdio.company_name`
2. `PrimeMatrixData-stdio.basic_info`
3. `Tianyancha.companyBaseInfo`
4. `PrimeMatrixData-stdio.risk_info`
5. `PrimeMatrixData-stdio.judicial_info`
6. `Tianyancha.risk`
7. 视情况补充：
   - `PrimeMatrixData-stdio.job_info`
   - `PrimeMatrixData-stdio.honor_info`
   - `PrimeMatrixData-stdio.ip_info`
   - `PrimeMatrixData-stdio.shareholder_info`

## OpenClaw 稳定调用路径

如果宿主机上的 bundle MCP 注入不稳定，优先直接用 `exec` 调插件内置桥脚本，不要空等超时。

推荐命令：

```bash
cd ~/.openclaw/extensions/aigroup-lead-discovery-openclaw
python3 scripts/mcp_compat/prime_matrix_stdio_bridge.py company_name '{"blur_name":"华为"}'
python3 scripts/mcp_compat/prime_matrix_stdio_bridge.py basic_info '{"company_name":"华为技术有限公司"}'
python3 scripts/mcp_compat/prime_matrix_stdio_bridge.py risk_info '{"company_name":"华为技术有限公司"}'
python3 scripts/mcp_compat/prime_matrix_stdio_bridge.py judicial_info '{"company_name":"华为技术有限公司"}'
python3 scripts/mcp_compat/tianyancha_stdio_bridge.py companyBaseInfo '{"companyName":"华为技术有限公司"}'
python3 scripts/mcp_compat/tianyancha_stdio_bridge.py risk '{"companyName":"华为技术有限公司"}'
```

规则：

- 如果直接工具可用，优先直接工具
- 如果直接工具不可用或宿主日志里出现 MCP timeout，立刻切到上面的 `exec + node` 路径
- 输出里要明确区分来自 PrimeMatrixData 和 Tianyancha 的事实

## 输出模板

### 企业确认
- 标准企业名称
- 成立时间 / 注册资本 / 法人 / 经营状态

### 正向线索
- 招聘、扩张、专利、荣誉、股东变化等

### 风险线索
- 司法、经营、异常、处罚、失信等

### 客户经理判断
- `建议跟进` / `建议观察` / `建议暂缓`
- 一句话说明原因

### 下一步动作
- 推荐联系切口
- 推荐补充核查项

## 规则

- 名称不确定时，不要跳过 `company_name`
- 初筛阶段强调“是否值得联系”，不要写成长篇尽调报告
- 风险与机会都要写，不能只报好消息
