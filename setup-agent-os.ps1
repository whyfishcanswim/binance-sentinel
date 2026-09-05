$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "Binance Sentinel - Agent OS / Skills Hub setup" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "This setup installs the official Binance Skills Hub into this project."
Write-Host "It does NOT ask for Binance credentials and does NOT enable trading."
Write-Host ""

function Refresh-Path {
    $machine = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
    $user = [System.Environment]::GetEnvironmentVariable("Path", "User")
    $env:Path = "$machine;$user"
}

# 1. Check Node.js 22+
$nodeCommand = Get-Command node -ErrorAction SilentlyContinue

if (-not $nodeCommand) {
    Write-Host "Node.js is not installed." -ForegroundColor Yellow
    Write-Host "Binance Skills Hub requires Node.js version 22 or higher."
    Write-Host ""

    $wingetCommand = Get-Command winget -ErrorAction SilentlyContinue
    if ($wingetCommand) {
        $answer = Read-Host "Install the current Node.js LTS with Windows Package Manager now? (Y/N)"
        if ($answer -match '^[Yy]$') {
            winget install OpenJS.NodeJS.LTS --accept-package-agreements --accept-source-agreements
            Refresh-Path
        } else {
            Write-Host "Setup stopped. Install Node.js 22+ and run this script again." -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "Windows Package Manager was not found." -ForegroundColor Red
        Write-Host "Install Node.js 22+ from https://nodejs.org and run this script again."
        exit 1
    }
}

$nodeVersionText = (& node --version).Trim()
$nodeMajor = [int](($nodeVersionText -replace '^v','').Split('.')[0])

Write-Host "Detected Node.js $nodeVersionText" -ForegroundColor Green

if ($nodeMajor -lt 22) {
    Write-Host "Node.js 22 or higher is required by Binance Skills Hub." -ForegroundColor Red
    Write-Host "Please upgrade Node.js and run this script again."
    exit 1
}

# 2. Check npx
$npxCommand = Get-Command npx -ErrorAction SilentlyContinue
if (-not $npxCommand) {
    Refresh-Path
    $npxCommand = Get-Command npx -ErrorAction SilentlyContinue
}

if (-not $npxCommand) {
    Write-Host "npx was not found after installing Node.js." -ForegroundColor Red
    Write-Host "Close PowerShell, open a new one, and run this script again."
    exit 1
}

Write-Host ""
Write-Host "Installing official Binance Skills Hub..." -ForegroundColor Yellow
Write-Host "The next command comes directly from Binance's Skills Hub README:"
Write-Host "npx skills add https://github.com/binance/binance-skills-hub" -ForegroundColor Cyan
Write-Host ""

# 3. Official Binance installation command
& npx skills add https://github.com/binance/binance-skills-hub

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Binance Skills Hub installation did not finish successfully." -ForegroundColor Red
    Write-Host "Review the message above, then run this script again."
    exit $LASTEXITCODE
}

Write-Host ""
Write-Host "Official Binance Skills Hub installation completed." -ForegroundColor Green
Write-Host ""
Write-Host "Verification:" -ForegroundColor Yellow

$possibleSkillPaths = @(
    ".agents\skills\binance\SKILL.md",
    ".codex\skills\binance\SKILL.md",
    ".claude\skills\binance\SKILL.md",
    ".gemini\skills\binance\SKILL.md",
    "skills\binance\SKILL.md"
)

$found = $false
foreach ($path in $possibleSkillPaths) {
    if (Test-Path $path) {
        Write-Host "Found Binance Skill: $path" -ForegroundColor Green
        $found = $true
    }
}

if (-not $found) {
    Write-Host "The installer completed, but Sentinel did not find the Skill in its common project paths." -ForegroundColor Yellow
    Write-Host "This can happen if the Skills CLI installed it for a specific agent runtime."
}

$binanceCli = Get-Command binance-cli -ErrorAction SilentlyContinue
if ($binanceCli) {
    Write-Host "binance-cli detected: $($binanceCli.Source)" -ForegroundColor Green
} else {
    Write-Host "binance-cli not detected. Sentinel will keep public REST as its data fallback." -ForegroundColor Yellow
    Write-Host "The official Binance Skill itself is still useful to compatible AI agent runtimes."
}

Write-Host ""
Write-Host "Next:" -ForegroundColor Yellow
Write-Host "  streamlit run dashboard.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "No Binance API key or account login was added by this setup." -ForegroundColor Green
