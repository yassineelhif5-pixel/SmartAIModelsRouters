 [CmdletBinding(SupportsShouldProcess = $true)]
param(
    [ValidateSet("Claude", "Codex", "GeminiCLI", "Copilot")]
    [string[]]$Hosts = @("Claude", "Codex", "GeminiCLI", "Copilot")
)
$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$skillNames = @("hif", "hifnode")
$hostPaths = @{
    Claude = Join-Path $HOME ".claude\skills"
    Codex = Join-Path $HOME ".agents\skills"
    GeminiCLI = Join-Path $HOME ".gemini\skills"
    Copilot = Join-Path $HOME ".copilot\skills"
}
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
foreach ($hostName in $Hosts) {
    $destinationRoot = $hostPaths[$hostName]
    if (-not (Test-Path -LiteralPath $destinationRoot)) {
        if ($PSCmdlet.ShouldProcess($destinationRoot, "Create directory")) {
            New-Item -ItemType Directory -Path $destinationRoot -Force | Out-Null
        }
    }
    foreach ($skillName in $skillNames) {
        $source = Join-Path $repoRoot "skills\$skillName"
        $destination = Join-Path $destinationRoot $skillName
        if (-not (Test-Path -LiteralPath (Join-Path $source "SKILL.md"))) {
            throw "Source skill is missing: $source\SKILL.md"
        }
        if (Test-Path -LiteralPath $destination) {
            $backup = "$destination.backup.$timestamp"
            if ($PSCmdlet.ShouldProcess($destination, "Back up existing skill")) {
                Move-Item -LiteralPath $destination -Destination $backup
                Write-Host "Backed up existing $hostName/$skillName to $backup"
            }
        }
        if ($PSCmdlet.ShouldProcess($destination, "Install HIF skill")) {
            Copy-Item -LiteralPath $source -Destination $destination -Recurse
            Write-Host "Installed $hostName/$skillName => $destination"
        }
    }
}
Write-Host ""
Write-Host "HIF instructions installed for: $($Hosts -join ', ')"
Write-Host "Start a new assistant session to load the skills."
Write-Warning "This installs skill instructions only, not the HIF orchestration backend or MCP gateway."
