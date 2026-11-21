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

& $venvPython -m pip install -e ".[providers]"
if ($LASTEXITCODE -ne 0) { throw "HIF package installation failed." }

$envFile = Join-Path $repoRoot ".env"
if (-not (Test-Path -LiteralPath $envFile)) {
    Copy-Item (Join-Path $repoRoot ".env.example") $envFile
    Write-Host "Created .env from .env.example. Add authorized provider model IDs and API keys."
}

$mcpExe = Join-Path (Split-Path -Parent $venvPython) "hif-mcp.exe"
$hifExe = Join-Path (Split-Path -Parent $venvPython) "hif.exe"

Write-Host ""
Write-Host "HIF runtime installed in $repoRoot\.venv"
Write-Host "Configure .env, then test with:"
Write-Host ("  " + $hifExe + " --help")
Write-Host ("  " + $hifExe + " usage")
Write-Host ("  " + $hifExe + " gateway")
Write-Host ""
Write-Host "Register HIF globally for Claude Code (all projects for this Windows user):"
Write-Host ('claude mcp add --scope user --transport stdio hif -- "' + $mcpExe + '"' )
Write-Host "claude mcp list"
Write-Host ""
Write-Host "Gemini CLI user-scope MCP registration:"
Write-Host ('gemini mcp add --scope user hif "' + $mcpExe + '"' )
Write-Host "gemini mcp list"
Write-Host ""
Write-Host "OpenAI Codex user MCP registration:"
Write-Host ('codex mcp add hif -- "' + $mcpExe + '"' )
Write-Host "codex mcp list"
Write-Warning "The installer does not create a Windows Service or expose a remote HTTP gateway."
