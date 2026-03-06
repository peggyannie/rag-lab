---
title: "NovelAI Studio 部署与功能迭代记录"
date: "2026-02-28"
tags: [codex-dialog, implementation, novelai-studio, aliyun, nextjs]
source: codex-chat
template: implementation
status: done
---

# NovelAI Studio 部署与功能迭代记录

## 目标

1. 完成阿里云 ECS 生产部署（Nginx + Docker + 域名 + HTTPS + CI/CD）。
2. 新增产品迭代：将“AI 一键生成世界观”从创建流程迁移到作品详情页。
3. 排查并修复 CI/CD 与构建问题。

## 实现方案

- 后端/前端/部署三线并行推进：
  - 部署链路：Docker Compose 生产编排 + Nginx 反向代理 + 证书脚本 + GitHub Actions SSH 发布。
  - 功能链路：简化创建作品流程，把 AI 世界观推演能力移动到作品详情页。
- 优先处理阻塞项：
  - 远程部署失败（非 git 目录、构建失败）。
  - 前端构建失败（`@/lib/utils` 缺失 + `.gitignore` 误忽略）。

## 关键改动

1. 部署与文档
- 完成阿里云 ECS 部署链路打通（站点可通过 DuckDNS 域名访问）。
- 补充并更新部署文档与 README。
- 增加 GitHub Actions 自动部署流程并迭代修复。

2. 前端功能迭代
- `project-wizard` 简化为基础信息创建，创建后直接进入作品详情。
- 在作品详情页新增“AI推演世界观”入口和弹窗：
  - 主角设定 / 金手指 / 境界体系输入
  - AI 一键构思
  - AI 一键推演世界观
  - SSE 进度反馈

3. 构建与仓库修复
- 恢复 `frontend/lib/utils.ts`（`cn` 工具函数）。
- 修复 `.gitignore`，确保 `frontend/lib/**` 被纳入版本控制。
- 通过 `frontend` 生产构建验证。

4. 分支与合并
- 在 `codex/aliyun-auto-deploy` 分支提交并推送改动。
- 处理合并到 `main` 时的冲突（`.gitignore`、`frontend/lib/utils.ts`）。
- 完成合并推送与本地分支清理。

## 关键命令
```bash
# 前端构建验证
cd frontend && npm run build

# 分支提交与推送
git add ...
git commit -m "feat(frontend): move AI bible generation to project detail"
git push origin codex/aliyun-auto-deploy

# 合并到 main
git checkout main
git pull --ff-only origin main
git merge --no-ff codex/aliyun-auto-deploy
git push origin main

# 冲突解决后再次验证
cd frontend && npm run build
```

## 验证结果

- 前端构建：通过。
- 功能迁移：已完成，入口位于作品详情页。
- 主分支状态：相关改动已合并至 `main`。

## 结论

本次会话完成了从部署、联调到功能迭代和发布的全链路推进，当前项目已具备稳定的生产部署基础。

## 后续动作

1. 继续观察 CI/CD 部署稳定性和回滚流程。
2. 按优先级推进下一批产品功能迭代。
