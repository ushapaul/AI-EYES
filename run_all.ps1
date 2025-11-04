# Run All (frontend + backend processes) for AI-EYES
# Usage: Right-click -> Run with PowerShell, or open PowerShell in repo root and run: .\run_all.ps1
# Notes:
# - This script opens three PowerShell windows:
#     1) Frontend (Vite) -> runs `npm install` if node_modules is missing, then `npm run dev`
#     2) Backend API -> ensures a Python venv exists under backend (creates .venv if needed), installs requirements, then runs app_simple.py
#     3) Multi-camera surveillance -> same venv handling, installs surveillance requirements, then runs multi_camera_surveillance.py
# - The script tries to automatically create venv and install requirements. It cannot install Node.js itself; if `npm` is missing it will notify you.
# - If your environment requires a specific Python executable (eg. py -3.10), the script will try `py -3.10` then fallback to `python`.

$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
if (-not $ScriptRoot) { $ScriptRoot = Get-Location }

# Helper to escape single quotes in paths for embedding in -Command string
function Escape-SingleQuote([string]$s) {
    return $s -replace "'","''"
}

# Kill any running Python processes from previous runs to avoid file lock issues during pip install
Write-Host "Checking for running Python processes from previous sessions..." -ForegroundColor Yellow
Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*AI eyes*" } | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1

# Create small helper scripts (temporary files) that each tab will execute. This makes quoting easier.
$frontendScript = Join-Path $ScriptRoot '._run_frontend.ps1'
$backendScript = Join-Path $ScriptRoot '._run_backend_api.ps1'
$surveilScript  = Join-Path $ScriptRoot '._run_multi_camera.ps1'

# Use actual path values (not variables) in the generated scripts to avoid undefined variable errors
$rootPath = $ScriptRoot
$backendPath = Join-Path $ScriptRoot 'backend'

Set-Content -Path $frontendScript -Value @"
Set-Location '$rootPath'
Write-Host '=== FRONTEND: starting in $rootPath ===' -ForegroundColor Cyan
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Warning 'npm (or Node.js) was not found in PATH. Please install Node.js from https://nodejs.org/ and re-run this script.'
    Read-Host -Prompt 'Press Enter to keep this window open (or Ctrl+C to close)'
} else {
    if (-not (Test-Path (Join-Path '$rootPath' 'node_modules'))) {
        Write-Host 'node_modules missing — running npm install...' -ForegroundColor Yellow
        npm install
        if (`$LASTEXITCODE -ne 0) { Write-Warning 'npm install failed. Please check the output and resolve dependency issues.'; Read-Host -Prompt 'Press Enter to keep this window open' }
    }
    Write-Host 'Starting Vite dev server (npm run dev)...' -ForegroundColor Green
    npm run dev
}
"@

$backendScriptContent = @"
Set-Location '$backendPath'
Write-Host '=== BACKEND API: starting ===' -ForegroundColor Cyan

# Find existing venv
`$pythonExe = `$null
`$venvPaths = @('.venv\Scripts\python.exe', 'venv\Scripts\python.exe', 'venv_fresh_py310\Scripts\python.exe')
foreach (`$vPath in `$venvPaths) {
    if (Test-Path `$vPath) {
        `$pythonExe = (Resolve-Path `$vPath).Path
        break
    }
}

# Create venv if not found
if (-not `$pythonExe) {
    Write-Host 'Creating new venv...' -ForegroundColor Yellow
    try {
        py -3.10 -m venv .venv
    } catch {
        python -m venv .venv
    }
    `$pythonExe = (Resolve-Path '.venv\Scripts\python.exe').Path
}

if (-not (Test-Path `$pythonExe)) {
    Write-Warning 'Failed to create venv. Please install Python and try again.'
    Read-Host 'Press Enter to exit'
    exit 1
}

Write-Host "Using: `$pythonExe" -ForegroundColor Green

# Install packages
Write-Host 'Installing packages...' -ForegroundColor Yellow
& `$pythonExe -m pip install --quiet --upgrade pip setuptools wheel
& `$pythonExe -m pip install --quiet -r requirements.txt
& `$pythonExe -m pip install --quiet -r requirements_surveillance.txt
& `$pythonExe -m pip install --quiet pymongo sendgrid PyJWT

Write-Host 'Starting backend API...' -ForegroundColor Green
& `$pythonExe app_simple.py

Write-Host ''
Write-Warning 'Backend stopped. Press Enter to close.'
Read-Host
"@
Set-Content -Path $backendScript -Value $backendScriptContent

$surveilScriptContent = @"
Set-Location '$backendPath'
Write-Host '=== MULTI-CAMERA: starting ===' -ForegroundColor Cyan

# Wait for backend to finish setup
Write-Host 'Waiting 10 seconds for backend setup...' -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Find venv (should exist from backend tab)
`$pythonExe = `$null
`$venvPaths = @('.venv\Scripts\python.exe', 'venv\Scripts\python.exe', 'venv_fresh_py310\Scripts\python.exe')
foreach (`$vPath in `$venvPaths) {
    if (Test-Path `$vPath) {
        `$pythonExe = (Resolve-Path `$vPath).Path
        break
    }
}

if (-not `$pythonExe) {
    Write-Warning 'No venv found. Please ensure backend API tab completed setup.'
    Read-Host 'Press Enter to exit'
    exit 1
}

Write-Host "Using: `$pythonExe" -ForegroundColor Green
Write-Host 'Starting multi-camera surveillance...' -ForegroundColor Green
& `$pythonExe multi_camera_surveillance.py

Write-Host ''
Write-Warning 'Surveillance stopped. Press Enter to close.'
Read-Host
"@
Set-Content -Path $surveilScript -Value $surveilScriptContent

# If Windows Terminal (wt.exe) is available, open three tabs in a single window; otherwise fall back to separate PowerShell windows.
if (Get-Command wt -ErrorAction SilentlyContinue) {
    $wtArgs = "new-tab powershell -NoExit -NoProfile -File `"$frontendScript`" ; new-tab powershell -NoExit -NoProfile -File `"$backendScript`" ; new-tab powershell -NoExit -NoProfile -File `"$surveilScript`""
    Start-Process -FilePath wt -ArgumentList $wtArgs
} else {
    Start-Process -FilePath powershell -ArgumentList '-NoExit','-NoProfile','-File',$frontendScript
    Start-Process -FilePath powershell -ArgumentList '-NoExit','-NoProfile','-File',$backendScript
    Start-Process -FilePath powershell -ArgumentList '-NoExit','-NoProfile','-File',$surveilScript
}

Write-Host "Launched 3 terminals (Windows Terminal used: $(Get-Command wt -ErrorAction SilentlyContinue -OutVariable wtCmd; if ($wtCmd) { 'Yes' } else { 'No' })): Frontend (vite), Backend API (app_simple.py), Multi-camera (multi_camera_surveillance.py)" -ForegroundColor Green
Write-Host "If any terminal reported missing tools (Node, Python), follow the messages in those windows to resolve them." -ForegroundColor Yellow
