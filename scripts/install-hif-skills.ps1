[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [ValidateSet("Claude", "Codex", "GeminiCLI", "Copilot", "Cursor", "Kimi", "Qwen")]
    [string[]]$Hosts = @("Claude", "Codex", "GeminiCLI", "Copilot", "Cursor", "Kimi", "Qwen")
)
$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$skillsRoot = Join-Path $repoRoot "skills"
$skillDirs = @(Get-ChildItem -LiteralPath $skillsRoot -Directory | Where-Object {
    Test-Path -LiteralPath (Join-Path $_.FullName "SKILL.md")
})
if ($skillDirs.Count -eq 0) { throw "No portable HIF skills found in $skillsRoot" }

$hostPaths = @{
    Claude = Join-Path $HOME ".claude\skills"
    Codex = Join-Path $HOME ".agents\skills"
    GeminiCLI = Join-Path $HOME ".gemini\skills"
    Copilot = Join-Path $repoRoot ".github\skills"
    Cursor = Join-Path $HOME ".cursor\skills"
    Kimi = Join-Path $HOME ".kimi-code\skills"
    Qwen = Join-Path $HOME ".qwen\skills"
}
$timestamp = "$(Get-Date -Format 'yyyyMMdd-HHmmss-fff')-$PID"
foreach ($hostName in $Hosts) {
    $destinationRoot = $hostPaths[$hostName]
    if (-not (Test-Path -LiteralPath $destinationRoot)) {
        if ($PSCmdlet.ShouldProcess($destinationRoot, "Create directory")) {
            New-Item -ItemType Directory -Path $destinationRoot -Force | Out-Null
        }
    }
    foreach ($skillDir in $skillDirs) {
        $destination = Join-Path $destinationRoot $skillDir.Name
        if (Test-Path -LiteralPath $destination) {
            $backup = "$destination.backup.$timestamp"
            if ($PSCmdlet.ShouldProcess($destination, "Back up existing skill")) {
                Move-Item -LiteralPath $destination -Destination $backup
                Write-Host "Backed up $hostName/$($skillDir.Name) to $backup"
            }
        }
        if ($PSCmdlet.ShouldProcess($destination, "Install HIF skill")) {
            Copy-Item -LiteralPath $skillDir.FullName -Destination $destination -Recurse
            Write-Host "Installed $hostName/$($skillDir.Name) => $destination"
        }
    }
}
Write-Host ""
Write-Host "Installed $($skillDirs.Count) HIF skills for: $($Hosts -join ', ')"
Write-Host "Start a new assistant session to load the skills."
Write-Host "GitHub Copilot skills are installed in the repository-level .github\skills directory."
Write-Host "Cursor, Kimi Code and Qwen Code use their native skill directories."
Write-Warning "This installs skill instructions only. It does not install the HIF runtime/MCP gateway or grant API access."
