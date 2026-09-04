<#
 ============================================================
  一键发布脚本（GitHub Pages）
  前置条件：已安装 GitHub CLI（gh），且已完成登录：
    gh auth login
  （登录会给出一次性设备码，用你的浏览器打开
   https://github.com/login/device 输入即可）

  用法：
    powershell -ExecutionPolicy Bypass -File scripts/publish.ps1
  可选参数：
    -RepoName portfolio   # 默认自动取 <用户名>.github.io（个人主页）
 ============================================================
#>
param(
  [string]$RepoName = ""
)

$ErrorActionPreference = "Stop"

# 1) gh 检查与登录状态
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
  Write-Host "[X] 未安装 GitHub CLI，请先安装：" -ForegroundColor Red
  Write-Host "    winget install -e --id GitHub.cli" -ForegroundColor Yellow
  exit 1
}
$who = gh api user --jq ".login" 2>$null
if (-not $who) {
  Write-Host "[!] 尚未登录 GitHub，开始设备码登录流程……" -ForegroundColor Yellow
  Write-Host "    请按提示：1) 复制一次性代码  2) 浏览器打开 https://github.com/login/device 输入" -ForegroundColor Cyan
  gh auth login --hostname github.com --git-protocol https --web
  $who = gh api user --jq ".login"
  if (-not $who) { Write-Host "[X] 登录未完成"; exit 1 }
}
Write-Host "[OK] GitHub 账号：$who" -ForegroundColor Green

# 2) 决定仓库名
if (-not $RepoName) { $RepoName = "$who.github.io" }
Write-Host "[>] 目标仓库：$RepoName"

# 3) 创建仓库并推送（已存在则直接推送）
$exists = gh repo view "$who/$RepoName" --json name --jq ".name" 2>$null
if (-not $exists) {
  gh repo create "$RepoName" --public --source . --remote origin --push
  Write-Host "[OK] 已创建并推送 $who/$RepoName" -ForegroundColor Green
} else {
  git remote remove origin 2>$null
  git remote add origin "https://github.com/$who/$RepoName.git"
  git push -u origin main
  Write-Host "[OK] 已推送到 $who/$RepoName" -ForegroundColor Green
}

# 4) 开启 GitHub Pages（由仓库内 .github/workflows/deploy.yml 自动部署）
gh api -X POST "repos/$who/$RepoName/pages" -f "build_type=workflow" --silent 2>$null
Write-Host "[OK] Pages 已开启（Actions 构建完成后生效，约 1~2 分钟）" -ForegroundColor Green

Write-Host ""
Write-Host "网站地址：https://$RepoName" -ForegroundColor Cyan
Write-Host "后台查看：https://github.com/$who/$RepoName/actions" -ForegroundColor Cyan
Write-Host "以后更新内容只需：git add .; git commit -m '...'; git push" -ForegroundColor Cyan
