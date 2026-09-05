# make_shortcut.ps1 - create desktop shortcut for Laike Browser (ASCII only).
# Target: tools\start_dsh.bat (Baidu homepage by default, CDP 9222). Icon: branding\laike_icon.ico
param(
  [string]$Root = "D:\AILee\office-agent-local\apps\dsh-browser"
)
$ErrorActionPreference = "Continue"
$bat = Join-Path $Root "tools\start_dsh.bat"
$ico = Join-Path $Root "branding\laike_icon.ico"
$name = "Laike Browser"
$desktop = [Environment]::GetFolderPath("Desktop")
$lnk = Join-Path $desktop ($name + ".lnk")
$ws = New-Object -ComObject WScript.Shell
$sc = $ws.CreateShortcut($lnk)
$sc.TargetPath = $bat
$sc.WorkingDirectory = Split-Path $bat
if (Test-Path $ico) { $sc.IconLocation = $ico }
$sc.Description = "Open Laike Browser (Baidu homepage, clean & fast)"
$sc.Save()
Write-Output ("shortcut created: " + $lnk)
