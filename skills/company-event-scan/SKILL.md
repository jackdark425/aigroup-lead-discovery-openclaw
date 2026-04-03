---
name: company-event-scan
description: 企业事件扫描技能。适用于“看看这家公司最近有没有融资、扩产、招投标、招聘、上市、出海、获奖、重大合作”等事件线索。优先结合 PrimeMatrixData-stdio 结构化信号与公开网页搜索，形成外拓触发器清单。
---

# 企业事件扫描

把企业近期外网动态转成客户经理可用的营销触发器。

## 目标

围绕“现在为什么联系这家公司”给出事件清单和营销切口。

## 工具优先级

1. `PrimeMatrixData-stdio.job_info`
2. `PrimeMatrixData-stdio.honor_info`
3. `PrimeMatrixData-stdio.ip_info`
4. `PrimeMatrixData-stdio.statistic_info`
5. `PrimeMatrixData-stdio.finance_info` 或 `stk_company_basic_info`（如适用）
6. 补充公开网页搜索，核对最新新闻、融资、合作、项目、招投标、扩产等信息

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
