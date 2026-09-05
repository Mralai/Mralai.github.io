# laike-assistant（来可助手 · 电脑版）

> 总纲见库级 `docs/15-来可助手DSH一体封装方案.md`。
> 定位：**开箱即用的本地 DSH** —— 把本机 DeepSeek Harness 全能力（Agent/工具/Cordis
> 插件生态/模型路由）与自研办公能力（OCR/知识库/公文/浏览器控制）一体封装为 Windows 应用，
> 优先电脑版；品牌：来可（docs/14），UI 宿主：来可浏览器（apps/dsh-browser）。

## 目录

| 路径 | 说明 | 状态 |
|---|---|---|
| `runtime/` | 内置 DSH 运行时（@deepseek-ai/dsh + profiles/web + Node 便携；不入库） | 规划（里程碑 A） |
| `plugins/laike-office/` | Cordis 插件：OCR/文档解析/知识库/公文/导出（移植 office-assistant core） | 规划（里程碑 B） |
| `plugins/laike-browser/` | Cordis 插件：封装 dsh_bridge 控制来可浏览器 | 规划（里程碑 B） |
| `pkg/` | 打包：启动编排器、首次向导、PyInstaller/NSIS 发行 | 规划（里程碑 A/C） |
| `docs/` | 里程碑 A/B/C 验收记录 | — |

## 里程碑

- A 环境封装：可复刻的 DSH 运行时目录 + 启动编排 + 独立端口 A/B 验证
- B Cordis 插件：laike-office / laike-browser 开发并注册进内置 web profile，会话冒烟
- C 安卓手机版（进行中）：C-1 局域网 serve（完成验证）→ C-2 手机启动页 PWA（完成验证）→ C-3 Capacitor APK + CI（下一步）
- C 白标发行（后续）：启动器 exe/图标/双版本
- D 手机版：远程/PWA 复用
