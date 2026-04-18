---
name: company-event-scan
description: 企业事件扫描技能。适用于“看看这家公司最近有没有融资、扩产、招投标、招聘、上市、出海、获奖、重大合作”等事件线索。优先结合 PrimeMatrixData 结构化信号与公开网页搜索，形成外拓触发器清单。
---

# 企业事件扫描

把企业近期外网动态转成客户经理可用的营销触发器。

## CN Lead-Gen Pre-flight（target 为中国公司时 MANDATORY）

当 target 是中国大陆 / 港股 / 中概股 entity（触发词：A股 / 港股 / 科创板 / 创业板 / 北交所 / 中概股 / H 股，或 `*.SH` / `*.SZ` / `*.BJ` / `*.HK` ticker，或公司中文名），**在开始本 skill 任何步骤之前**先加载并遵循 [`cn-lead-safety`](../cn-lead-safety/SKILL.md) skill 的 5 条 Rule：

- **Rule 1** 中文 UTF-8 literal，禁 `\uXXXX` escape
- **Rule 2** 公司名 / 术语 lexicon lookup
- **Rule 3** 数据源 tier：T1 巨潮/Tushare/交易所 > T2 天眼查/工商 > T3 FMP/Finnhub > T4 财经媒体
- **Rule 4** 每个硬数字**内联** source citation（来源：xxx 年报 / Tushare / 巨潮 / 东方财富 ...）
- **Rule 5** 数据不可得标 "N/A / 数据不可得"，**禁** fabricate

交付前必须跑 `python3 ../cn-lead-safety/scripts/verify_intelligence.py <events.md>`，exit 0 方可交。

## 目标

围绕“现在为什么联系这家公司”给出事件清单和营销切口。

## 工具优先级

1. `PrimeMatrixData.job_info`
2. `PrimeMatrixData.honor_info`
3. `PrimeMatrixData.ip_info`
4. `PrimeMatrixData.statistic_info`
5. `PrimeMatrixData.finance_info` 或 `stk_company_basic_info`（如适用）
6. 补充公开网页搜索，核对最新新闻、融资、合作、项目、招投标、扩产等信息

## OpenClaw 稳定调用策略

如果 PrimeMatrixData 没有注入成功：

- 先用 web / browser / search 搜最近 90 天新闻、招投标、招聘、专利、荣誉
- 对上市公司补 `aigroup-market-mcp` / `aigroup-fmp-mcp` 的公告与财务事件
- 不要因为单一数据源失败就中断扫描

## 输出模板

### 关键事件
- 事件
- 发生时间
- 对客户经营意味着什么

### 可营销切口
- 资金需求
- 结算与现金管理
- 供应链金融
- 员工代发 / 薪酬 / 福利
- 国际业务 / 出海 / 汇率

### 优先级
- `高`
- `中`
- `低`

## 规则

- 没有时间信息的事件要标明“时间待核”
- 不把单条招聘信息夸大成融资结论
- 结论要贴近客户经理动作，而不是泛泛行业评论
