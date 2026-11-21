[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

$pythonLauncher = Get-Command py -ErrorAction SilentlyContinue
if ($pythonLauncher) {
    & py -3.12 --version
    if ($LASTEXITCODE -ne 0) {
        throw "Python 3.12 is required. Install it from python.org, then rerun this script."
    }
    & py -3.12 -m venv .venv
}
else {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) {
        throw "Python 3.12+ was not found. Install Python, then rerun this script."
    }
    $versionText = & python --version
    if ($versionText -notmatch "Python 3\.(1[2-9]|[2-9][0-9])") {
        throw "Python 3.12 or newer is required. Detected: $versionText"
    }
    & python -m venv .venv
}

$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $venvPython)) {
    throw "Virtual environment creation failed: $venvPython"
}

& $venvPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "pip upgrade failed." }

& $venvPython -m pip install -e ".[dev]"
if ($LASTEXITCODE -ne 0) { throw "HIF package installation failed." }

$envFile = Join-Path $repoRoot ".env"
if (-not (Test-Path -LiteralPath $envFile)) {
    Copy-Item (Join-Path $repoRoot ".env.example") $envFile
    Write-Host "Created .env from .env.example. Add your authorized provider model IDs and API keys."
}

Write-Host ""
Write-Host "HIF runtime installed in $repoRoot\.venv"
Write-Host "Configure .env, then test with:"
Write-Host "  .\.venv\Scripts\hif.exe --help"
Write-Host "  .\.venv\Scripts\hif.exe mcp"
Write-Host ""
Write-Host "For user-wide Claude Code MCP registration:"
Write-Host '  claude mcp add --scope user --transport stdio hif -- "' + $venvPython + '\..\hif-mcp.exe"'
Write-Warning "The installer does not create a Windows Service or expose a remote HTTP gateway."
