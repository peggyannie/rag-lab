---
title: "obsidian-dialog-export 模板路由优化"
date: "2026-02-28"
tags: [codex-dialog, implementation]
source: codex-chat
template: implementation
status: done
---

# obsidian-dialog-export 模板路由优化

## 目标
将 `obsidian-dialog-export` 技能完善为可稳定自动路由的模板体系，并沉淀可回归验证的规则。

## 实现方案
基于技能文档与模板文件做增量重构：
- 新增模板目录并落地多模板文件。
- 在技能规则中定义自动路由优先级与冲突决策。
- 通过示例与回归测试用例固化行为预期。

## 关键改动
- 完成 7 个模板文件落地：`troubleshooting`、`implementation`、`discussion`、`retrospective`、`adr`、`daily-log`、`knowledge-card`。
- 在技能文档中加入并迭代路由策略：
  - 去除“手动指定模板置顶”。
  - 最终定稿为：`输入语义+关键词` 优先，`上下文路由` 次之，最后默认 `implementation`。
- 补充路由示例与回归测试集（含泛化输入与弱上下文场景）。
- 补充 `daily-log` 的输出模式规则：未显式要求 `new/overwrite` 时优先 `append`。
- 补充多语义命中时的裁决顺序，避免歧义。

## 关键命令
```bash
# 主要操作
apply_patch
rg -n "..." /Users/xuanling/.agents/skills/obsidian-dialog-export/SKILL.md
nl -ba /Users/xuanling/.agents/skills/obsidian-dialog-export/SKILL.md
```

## 验证结果
- 路由规则已与目标一致：`输入语义+关键词 > 上下文 > 默认 implementation`。
- 示例与回归用例覆盖常见输入、上下文补全与冲突场景。
- 模板与技能文档结构一致，可直接用于后续导出任务。

## 结论
本轮已将技能升级为“自动路由主导”的可维护模板体系，满足“无需知道模板名也可正确落笔记”的使用方式。

## 后续动作
1. 后续真实导出若出现误判，优先补充到回归测试案例。
2. 可增加一组“反例测试”验证相近语义下的边界路由行为。
