# 游戏来 · 个人作品站

> 深色科技风的程序员个人作品展示站：作品集、开源源码、免费软件下载。

- 基于开源模板 **[DevPortfolio](https://github.com/RyanFitzgerald/devportfolio)**（Astro + Tailwind CSS v4，MIT）深度定制
- 深色科技风主题：代码符号网格、霓虹强调色、等宽字体点缀、中文排版优化
- **全部内容单文件配置**：`src/config.ts`
- 内置「下载中心」，自动发布到 GitHub Pages（CI 已配好），免费、免备案
- 字体自托管（IBM Plex Mono），不依赖 Google Fonts，国内访问稳定

## 快速开始（本地预览）

```bash
npm install        # 安装依赖
npm run dev        # 本地开发，默认 http://localhost:4321
npm run build      # 生产构建，产物输出到 dist/
npm run preview    # 本地预览生产构建
```

## 修改网站内容（只改一个文件）

打开 **`src/config.ts`**，所有字段都有中文注释：

| 想改什么 | 对应字段 |
| --- | --- |
| 网站署名（页头/页脚/Hero） | `name`（当前：「游戏来」） |
| 职业标签、简介、口号 | `title` / `description` / `heroTagline` |
| 主题色 | `accentColor`（如 `#22d3ee` 青、`#a78bfa` 紫） |
| 社交链接 | `social`（留空 `""` 即不显示） |
| 关于我 / 技能标签 | `aboutMe[]` / `skills[]` |
| 作品卡片 | `projects[]`（支持 `github` / `demo` / `download` 三个按钮） |
| 下载中心条目 | `downloads[]`（把文件放进 `public/files/`，登记名称/版本/大小） |
| 经历 / 教育 | `experience[]` / `education[]` |

> 注意：当前站点处于「示例数据」状态（`demoMode: true`），
> 页面会标注黄色「示例数据」徽标。把真实内容填好后，把 `demoMode` 改成
> `false` 即可。

## 上线部署

- **首选：GitHub Pages（免费）** → 阅读 [`docs/GitHub-Pages发布手册.md`](docs/GitHub-Pages发布手册.md)，然后一条命令：
  ```powershell
  powershell -ExecutionPolicy Bypass -File scripts\publish.ps1
  ```
- **绑定自己的域名 / 国内加速** → [`docs/域名购买与加速指南.md`](docs/域名购买与加速指南.md)
- **云服务器部署（含 ICP 备案流程）** → [`docs/云服务器部署指南.md`](docs/云服务器部署指南.md)（附 `deploy/nginx.conf.example`）

日常更新内容：改完 `src/config.ts` 后 `git add . && git commit -m "更新" && git push`，
CI 约 1 分钟自动重新发布。

## 目录结构

```
portfolio/
├── public/
│   ├── files/               # 下载中心的小文件（大文件用 GitHub Releases）
│   └── favicon.svg
├── src/
│   ├── components/          # Astro 组件（Header/Hero/About/Projects/Downloads/...）
│   ├── pages/               # index.astro（首页）、404.astro
│   ├── styles/global.css    # 全局样式与主题字体
│   └── config.ts            # ★ 站点内容配置（改这里）
├── .github/workflows/deploy.yml   # GitHub Pages 自动发布
├── docs/                    # 发布 / 域名 / 服务器 中文手册
├── scripts/publish.ps1      # 一键发布脚本
├── deploy/nginx.conf.example      # 服务器 Nginx 示例配置
├── astro.config.mjs         # Astro 配置（含部署路径自动适配）
└── package.json
```

## 致谢与许可

- 主题上游：[RyanFitzgerald/devportfolio](https://github.com/RyanFitzgerald/devportfolio)（MIT）
- 图标：[Tabler Icons](https://tabler.io/icons)
- 字体：IBM Plex Mono（[@fontsource/ibm-plex-mono](https://www.npmjs.com/package/@fontsource/ibm-plex-mono)，OFL 许可）
- 本项目整体以 **MIT** 许可发布，详见 `LICENSE.md`（含上游版权声明）。

## Projects

- [来可 · 本地 Agent 应用开源（office-agent-local）](/office-agent-local/) — 来可助手 / 来可浏览器 / 办公 AI 工具（净化公开快照）
