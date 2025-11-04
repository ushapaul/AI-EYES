Set-Location 'C:\Users\Lenovo\Desktop\AI eyes'
Write-Host '=== FRONTEND: starting in C:\Users\Lenovo\Desktop\AI eyes ===' -ForegroundColor Cyan
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Warning 'npm (or Node.js) was not found in PATH. Please install Node.js from https://nodejs.org/ and re-run this script.'
    Read-Host -Prompt 'Press Enter to keep this window open (or Ctrl+C to close)'
} else {
    if (-not (Test-Path (Join-Path 'C:\Users\Lenovo\Desktop\AI eyes' 'node_modules'))) {
        Write-Host 'node_modules missing — running npm install...' -ForegroundColor Yellow
        npm install
        if ($LASTEXITCODE -ne 0) { Write-Warning 'npm install failed. Please check the output and resolve dependency issues.'; Read-Host -Prompt 'Press Enter to keep this window open' }
    }
    Write-Host 'Starting Vite dev server (npm run dev)...' -ForegroundColor Green
    npm run dev
}
