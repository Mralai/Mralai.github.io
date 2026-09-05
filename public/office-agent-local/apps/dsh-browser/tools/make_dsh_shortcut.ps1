# make_dsh_shortcut.ps1 - create desktop shortcut "Laike Browser - DSH Web"
# opens DSH Web (http://127.0.0.1:3080) inside our browser (app mode, CDP 9222).
# ASCII-only source.
param(
  [string]$Root = "D:\AILee\office-agent-local\apps\dsh-browser",
  [string]$Python = "C:\Users\Administrator\AppData\Local\Programs\Python\Python310\python.exe"
)
$ErrorActionPreference = "Continue"
$pyw = [System.IO.Path]::ChangeExtension($Python, ".exe").Replace("python.exe", "pythonw.exe")
if (-not (Test-Path $pyw)) { $pyw = $Python }
$bridge = Join-Path $Root "tools\dsh_bridge.py"
$ico = Join-Path $Root "branding\laike_icon.ico"
$name = "Laike Browser - DSH Web"
$desktop = [Environment]::GetFolderPath("Desktop")
$lnk = Join-Path $desktop ($name + ".lnk")
$ws = New-Object -ComObject WScript.Shell
$sc = $ws.CreateShortcut($lnk)
$sc.TargetPath = $pyw
$sc.Arguments = "`"$bridge`" --port 9222 dsh --url http://127.0.0.1:3080 --app-mode"
$sc.WorkingDirectory = Split-Path $bridge
if (Test-Path $ico) { $sc.IconLocation = $ico }
$sc.Description = "Open DSH Web in Laike Browser (CDP 9222)"
$sc.Save()
Write-Output ("dsh shortcut created: " + $lnk)
