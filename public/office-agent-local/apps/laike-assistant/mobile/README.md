# 来可助手 · 安卓壳（Capacitor）构建说明

`mobile/` 为 Capacitor 安卓壳工程：应用名 **来可助手**，图标为品牌"来"（adaptive 前景/背景
已替换），Web 内容 = 手机启动页（`web/`：填电脑地址→连接 DSH）。

## 目录

```
mobile/
├── web/                  ← 启动页（PWA：index.html/manifest/图标）【入库·来源】
├── capacitor.config.json ← appId com.laike.assistant.mobile / appName 来可助手 / webDir web
├── package.json / package-lock.json  ← @capacitor/core·cli·android（lock 入库）
├── node_modules/         ← 不入库
└── android/              ← 平台工程（不入库，由 cap add android 生成）
```

## 本机构建（需要 Android SDK/JDK17）

```powershell
cd apps\laike-assistant\mobile
npm ci
npx cap add android        # 首次
npx cap sync android       # web/图标改动后同步
cd android
.\gradlew assembleDebug    # 产出 app\build\outputs\apk\debug\app-debug.apk
```

## 云构建（推荐：无本机 SDK）

仓库推送到 GitHub 后，Actions → “Build Laike Assistant Android APK” → Run workflow
（或推送 `mobile-*` tag）。构建脚本见 `.github/workflows/build-android.yml`，
产物 artifact：`app-debug.apk`。

## 安装与使用

1. APK 传到手机安装（允许未知来源）；
2. 电脑运行：`laike_runner serve --home %LOCALAPPDATA%\LaikeAssistant\home --port 3085 --listen-port 3086`
3. 打开 App（启动页）→ 填电脑 `lan_url` → 连接 → 进入 DSH（或浏览器直接访问同地址）。

## 说明

- android/ 不入库（Capacitor 可再生成）；web 是唯一前端来源，改完 `cap sync`。
- adaptive 图标前景带 33% 安全边距；要换品牌图请替换
  `apps/dsh-browser/branding/laike_icon_512.png` 后重跑 mipmap 生成脚本（见提交历史/可复用说明）。
