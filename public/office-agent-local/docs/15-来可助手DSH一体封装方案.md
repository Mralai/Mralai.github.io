# 15 · 来可助手（电脑版）= 本地 DSH 全能力一体封装 · 方案

> 决策（2026-09-05）：将 office-assistant 升级迭代为 **来可助手（Laike Assistant）**——
> 目标是把本机已部署的 **DeepSeek Harness（DSH）全能力**（Agent/会话/工具/Cordis 插件生态/
> 模型路由/浏览器自动化/vision-router 等）**完整嵌入**，并**把我们已开发的办公能力
> （OCR/文档解析/知识库/公文/浏览器控制）做成 DSH 的 Cordis 插件**注册进 DSH，
> 实现"开箱即用 DSH"。**优先电脑版（Windows）**；手机版为后续（同 UI 走 PWA/远程）。

## 1. 关键事实（已本机核实）

| 项 | 结论 |
|---|---|
| DSH 许可 | `@deepseek-ai/dsh` **MIT**（可商用嵌入/再发行，保留版权声明）|
| 运行时 | Node v24 已装；`dsh` CLI 0.1.1-rc.2；`dsh web` 启动 GUI（127.0.0.1:3080）|
| Web 插件栈 | `~/.dsh/profiles/web`：bundles = dsh-base + dsh-web-app + dshmarket + dsh-find-plugin + dsh-balance-plugin + dsh-vision-router + dsh-computer-use |
| 模型配置 | `~/.dsh/settings.yaml`：agent-default-model=deepseek-vision / deepseek-v4-flash；providers 含 ollama(本地) 等；凭据在 .credentials.yaml |
| Agent 预设 | `~/.dsh/.agent-presets/<id>/`（agent.cordis.yml + preset.yml）；当前会话 default=cordis |
| 体积预算 | @deepseek-ai/dsh 195MB + profiles 69MB（pnpm 布局）+ Node 便携 ~30MB + 应用壳 ≈ 解包 400–600MB / zip 250–350MB |
| 无头通道 | `dsh --profile headless` 存在但当前缺少 deepseek-vision provider 适配器（插件栈不全）→ 集成以 **完整 web profile** 为主，无头通道列为增强 |
| 封装形态 | 无需重写 DSH：做「启动编排器 + 插件注册 + 白标宿主」，DSH 本体原样运行 |

## 2. 产品形态（电脑版「来可助手」）

```
来可助手（Windows 应用 / 解压即用目录或单文件启动器）
├── dsh/                  ← 内置 DSH 运行时：@deepseek-ai/dsh + profiles(web) + settings 初始化
├── plugins/              ← 我们开发的 Cordis 插件（注册进 DSH web profile）
│   ├── laike-office      ← OCR/文档解析/知识库/公文模板/导出（office-assistant 能力移植为工具）
│   └── laike-browser     ← dsh_bridge 控制来可浏览器（封装已有 CDP 控制桥）
├── runtime/browser       ← 来可浏览器（Thorium 基座）作为 DSH Web 的宿主窗口
├── LaikeAssistant.exe    ← 启动编排：起 dsh web → 开浏览器(DSH) → 托盘/状态
└── 白标：图标/窗口名/欢迎语（web UI 覆盖，见 §5 边界）
```

工作方式：
- 用户双击来可助手 → 自动启动内置 DSH（web profile，端口可配）→ 来可浏览器打开 DSH 界面；
- 对话即 DSH Agent 会话：**DSH 原有全部能力与插件都在**（电脑控制、OCR 上传、插件市场、模型切换）；
- 我们的办公工具以 **Tool** 形式出现在对话中（“上传报销单图片→OCR→填入表单”等），
  由 laike-office / laike-browser 插件提供；
- 一键“开箱即用”：无需用户安装 Node/npm/模型——首次运行向导仅需填 API Key（或连本地 ollama）。

## 3. 复用与待开发资产

| 资产 | 来源 | 处置 |
|---|---|---|
| DSH 本体 + web 插件栈 | 本机 `~/.dsh/profiles/web` 与全局 @deepseek-ai/dsh | 封装复制/初始化为内置运行时（含 pnpm 依赖处理） |
| 来可浏览器 + dsh_bridge | apps/dsh-browser | UI 宿主与浏览器工具插件后端 |
| OCR/KB/文档解析逻辑 | apps/office-assistant/src/core | 移植为 Cordis 插件（laike-office）|
| 公文模板 | apps/office-assistant/src/templates | 随 laike-office 打包 |
| 办公 Agent 预设 | 新写 | `来可办公` preset（agent.cordis.yml：persona+默认工具）|
| 品牌（来可） | docs/14 + branding | 白标图标/标题/欢迎语 |

## 4. 里程碑

- **A. 环境封装**：抽取"DSH 运行时 + web profile + Node"为可随包复刻的目录与初始化脚本；
  启动编排器（起/停/端口/首次向导）；本机 A/B 验证（独立端口起第二份 DSH 不冲突）。
- **B. Cordis 插件**：按 cordis-plugin-development 流程开发 laike-office 与 laike-browser
  （先 host 工具，UI Slot 视需要）；注册进内置 web profile；会话内冒烟（OCR/浏览器/公文）。
- **C. 白标与发行**：图标/窗口标题/欢迎语覆盖；PyInstaller/NSIS 打包 exe；签名与杀软白名单；
  双版本（国内版与商店版沿用 docs/13 套路）。
- **D. 手机版**：同一 DSH 实例远程访问（内网/隧道）或来可浏览器安卓壳。

## 5. 边界与风险（如实）

1. **profiles 依赖为 pnpm 布局**：封装需整链复制（robocopy 跟随链接）或首次运行用 pnpm deploy/install；
   体积与复制耗时需实测（列为 A 步验收项）。
2. **白标深度受限**：dsh-web-app 的品牌化（标题/图标/主题色）走插件主题/slot；若官方未暴露足够定制面，
   白标将限于"窗口名+图标+欢迎语+默认页"，主体 UI 保留 DSH 原生（并保留其署名，MIT 义务）。
3. **模型凭据**：DSH 对话需要模型通道（用户 DeepSeek key 或本地 ollama）；封装不含任何密钥，
   首次向导收集并写入用户自己的 settings/credentials（或复用本机已有 .dsh）。
4. **版本跟进**：DSH 升级后需重新封装（跟进流程文档化）。
5. office-assistant 的独立 Web UI 在来可助手中退居二线（能力并入插件）；旧 releases 仍可独立使用。

## 6. 目录约定

```
apps/laike-assistant/
├── README.md             ← 应用自述（本文件入口见仓库 docs/15）
├── runtime/              ← 封装运行时（内置 DSH/Node/浏览器，不入库）
├── plugins/              ← 自研 Cordis 插件源码（入库）
│   ├── laike-office/
│   └── laike-browser/
├── pkg/                  ← 打包脚本与发行（exe/目录/zip）
└── docs/                 ← 本应用记录（A/B/C 里程碑验收）
```
