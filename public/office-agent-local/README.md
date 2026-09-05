# 来可 · 本地 Agent 应用开源（office-agent-local 净化版）

> 从开发者本地应用库提取的开源快照：三个应用 + 品牌规范。完整代码与历史见开发者本地；本页为可公开的技术与代码展示。

## 应用

| 应用 | 说明 | 目录 |
|---|---|---|
| 来可助手 Laike Assistant | 本地 DSH 全能力一体封装（电脑版）+ 安卓手机版（局域网 serve + PWA/启动页 + Capacitor 壳 + CI 云构建） | apps/laike-assistant |
| 来可浏览器 Laike Browser | Thorium(BSD-3) 二次集成浏览器：直达默认页/干净无弹窗/CDP 自动化口 | apps/dsh-browser |
| 办公 AI 助手（历史独立包） | 离线 OCR/知识库/公文/表格（并入来可助手路线） | （另行公开） |

## 结构

- apps/dsh-browser：浏览器（tools/dsh_bridge 控制桥、branding、tests）
- apps/laike-assistant：来可助手（pkg/laike_runner 编排器、plugins/laike-tools Cordis 插件、mobile 手机壳）
- docs/：技术文档与 FAQ
- 首页 index.html：应用总览图

## 许可
- 本仓库自研代码：Apache-2.0（见 LICENSE）
- 上游 Thorium：BSD-3-Clause（见 apps/dsh-browser/NOTICE.txt）
- DSH(@deepseek-ai/dsh) 为 MIT；嵌入用途见 apps/laike-assistant 文档

## 手机版构建
Capacitor 壳 + GitHub Actions 云构建（JDK17+Node），见 apps/laike-assistant/mobile/README.md。
