# 来可助手 · 里程碑 A 验收：DSH 环境封装（2026-09-06）

目标：把本机 DSH 运行时做成可随来可助手复刻的目录与初始化器；验证"第二份独立 DSH
实例"可用（web profile 全插件栈）；产出启动编排器与首启向导骨架。

## 1. 关键机制发现（可复刻性结论）

| 发现 | 结论 |
|---|---|
| profile 依赖布局 | `~/.dsh/profiles/node_modules` 的 **164 项是 Junction**，全部指向「正在执行的 @deepseek-ai/dsh 包」的 `node_modules`（boot 的 installation-fallback 自动维护） |
| 复刻规则 | **不要复制 profiles/node_modules**；boot 启动时会按需自动重建全部 junction（healProfilesModuleFallback） |
| 必须随包 | `profiles/web/` 清单（package.json/pnpm-workspace/cordis.yml/cordis.patch.yml 等）**+ web/node_modules（69MB 实体）** + `settings.yaml` + `.agent-presets/` |
| 凭据 | `.credentials.yaml` **不入模板**（首启向导由用户提供，refs: {DEEPSEEK_API_KEY: …} 格式） |
| 模板体积 | **69MB**（实测 init 后 home ≈72MB）——远小于"整拷 441MB"方案 |
| 许可 | @deepseek-ai/dsh 为 MIT（可商用嵌入，保留声明） |

## 2. 验证记录（本机实测 PASS）

1. 复刻实例（verify-home，精简布局）在 **3095** 启动：首页 200（313KB），日志
   `dsh web: http://127.0.0.1:3095`，**自动读取 DEEPSEEK_API_KEY（file）**，额度监控初始化 ✓
2. boot 自动重建 **164 junctions**（与主实例一致）✓
3. 主实例 **3080 全程无冲突**（双实例并行 200）✓
4. 编排器冒烟（clean template 72MB → init → start → status）：
   `init-home ok(72.1MB)` → `start ok pid=9780` → `status ok` ✓
5. 清理：验证实例已停、含凭据的 verify-home 已删除、孤儿进程已回收；主 3080 正常。

## 3. 产物

| 路径 | 说明 |
|---|---|
| `runtime/template-home/`（不入库） | 可复刻基线模板：profiles/web 清单+依赖、settings.yaml、.agent-presets；无凭据/无缓存/无 profiles/node_modules |
| `pkg/laike_runner.py` | 编排器：`init-home / start / status / stop / open`（默认 home=%LOCALAPPDATA%\LaikeAssistant\home，默认端口 3085；robocopy 加速；pidfile+端口回收） |
| `docs/A-环境封装.md`（本文件） | 验收记录 |

## 4. 遗留/下一步

- 首启向导（凭据采集→写 .credentials.yaml、端口选择）→ 与「里程碑 B 插件」一同做
- 产品封装：内置 @deepseek-ai/dsh（195MB）+ 本模板 + Node 便携 → 启动编排 exe
  （docs/15 §4 路线 A→C 的 A 步其余部分）
- 后续 B：laike-office / laike-browser Cordis 插件注册进该 profile（web/cordis.patch.yml 增补 + bundle 引用）
