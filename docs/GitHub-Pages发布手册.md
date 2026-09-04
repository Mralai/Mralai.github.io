# GitHub Pages 发布手册（免费、免备案、首选上线方式）

> 目标：让网站上线到 `https://<你的GitHub用户名>.github.io/`
> 全程免费，无需服务器、无需域名、无需备案。

---

## 第 1 步：准备 GitHub 账号（约 5 分钟）

1. 打开 https://github.com/signup ，用邮箱注册（可用 QQ 邮箱）。
2. 到邮箱收验证码完成验证。
3. 记住你的**用户名（username）**，例如 `youxilai`。
4. 可选但强烈建议：设置 → Password 下开启 **2FA 两步验证**。

> 登录密码是敏感信息：请勿在聊天工具里继续发送密码；
> 发布完成后建议在 GitHub → Settings → Password 修改一次密码。

---

## 第 2 步：一键发布（推荐，已内置脚本）

本机已安装 GitHub CLI（`gh`）。在项目根目录执行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\publish.ps1
```

脚本会自动完成 4 件事：

| 步骤 | 说明 |
| --- | --- |
| ① 登录 | 若未登录会进入设备码流程：复制一次性代码 → 打开 https://github.com/login/device 输入 → 授权 |
| ② 建仓 | 自动创建 **`<你的用户名>.github.io`** 公开仓库并推送全部代码 |
| ③ 发布 | 仓库内置 `.github/workflows/deploy.yml`，推送即触发构建 |
| ④ 开启 Pages | 自动打开 GitHub Pages（source = GitHub Actions） |

构建约 1~2 分钟。完成后访问：

```
https://<你的用户名>.github.io/
```

Actions 状态与日志：`https://github.com/<用户名>/<仓库>/actions`

> 仓库名不是 `用户名.github.io` 也可以（例如 `portfolio`），
> 脚本加了 `-RepoName portfolio` 参数支持；两种模式构建路径都自动适配，
> 无需手动改配置。普通仓库模式网址会带 `/仓库名` 前缀。

---

## 手工方式（不用脚本时）

```bash
# 1. 登录
gh auth login

# 2. 建仓并推送（仓库名务必是 <用户名>.github.io）
gh repo create <用户名>.github.io --public --source . --remote origin --push

# 3. 打开仓库 Settings → Pages → Source 选 "GitHub Actions"
```

---

## 以后如何更新网站内容

改完内容（主要改 `src/config.ts`）后：

```bash
git add .
git commit -m "更新内容"
git push
```

推送后 Actions 自动重新构建发布，约 1 分钟生效。**不需要任何服务器操作。**

---

## 常见问题

**Q1：网站打不开 / 404？**
- 检查 Actions 是否绿色通过（`仓库 → Actions` 页面）；
- 首次构建需 1~2 分钟，请等待后刷新；
- 确认仓库 Settings → Pages → Build and deployment 来源是 **GitHub Actions**。

**Q2：样式错乱或图片丢失？**
- 确认本地 `npm run build` 无报错；CI 与本地 node 版本均为 22。

**Q3：GitHub Pages 在国内访问慢/偶尔打不开？**
- 这是正常现象（Pages 服务器在境外）。对策见《域名购买与加速指南》：
  配合国内 CDN，或按《云服务器部署指南》迁到香港/大陆服务器。

**Q4：想用自己的域名（如 youxilai.cn）？**
- 见《域名购买与加速指南》第 5 节「绑定自定义域名」。
