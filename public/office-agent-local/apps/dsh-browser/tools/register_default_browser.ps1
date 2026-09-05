# register_default_browser.ps1 - register "Laike Browser" as a system default-app
# candidate (ProgID + Capabilities + RegisteredApplications), then open the
# Windows default-apps settings page for the one-click user confirmation.
# ASCII-only source. Requires the runtime Thorium at the default location.
param(
  [string]$Root = "D:\AILee\office-agent-local\apps\dsh-browser"
)
$ErrorActionPreference = "Continue"
$exe = Join-Path $Root "runtime\thorium-win\thorium.exe"
if (-not (Test-Path $exe)) { Write-Output "ERR: thorium.exe not found at $exe"; exit 1 }
$progId = "LaikeBrowserHTML"
$appName = "Laike Browser"

# 1) ProgID (open http/https links with our browser)
$base = "HKCU:\Software\Classes\$progId"
New-Item -Path $base -Force | Out-Null
Set-ItemProperty -Path $base -Name "(default)" -Value "Laike Browser HTML Document"
New-Item -Path "$base\DefaultIcon" -Force | Out-Null
Set-ItemProperty -Path "$base\DefaultIcon" -Name "(default)" -Value "`"$exe`,0`""
New-Item -Path "$base\shell\open\command" -Force | Out-Null
Set-ItemProperty -Path "$base\shell\open\command" -Name "(default)" -Value "`"$exe`" `"%1`""

# 2) Capabilities (make the app visible in default-apps list)
$cap = "HKCU:\Software\LaikeBrowser\Capabilities"
New-Item -Path "$cap\URLAssociations" -Force | Out-Null
Set-ItemProperty -Path $cap -Name "ApplicationName" -Value $appName
Set-ItemProperty -Path "$cap\URLAssociations" -Name "http" -Value $progId
Set-ItemProperty -Path "$cap\URLAssociations" -Name "https" -Value $progId

# 3) RegisteredApplications
New-Item -Path "HKCU:\Software\RegisteredApplications" -Force | Out-Null
Set-ItemProperty -Path "HKCU:\Software\RegisteredApplications" -Name $appName -Value "Software\LaikeBrowser\Capabilities"

Write-Output "registered ProgID=$progId app=$appName exe=$exe"

# 4) Show current default and open the settings page for the final user click
$cur = (Get-ItemProperty "HKCU:\Software\Microsoft\Windows\Shell\Associations\UrlAssociations\https\UserChoice" -ErrorAction SilentlyContinue).ProgId
Write-Output "current https default: $cur"
Write-Output "opening default apps settings - choose '$appName' under Web browser"
Start-Process "ms-settings:defaultapps"
Write-Output "done"
