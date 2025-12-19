# Auto-Claude Startup Script
# One-command startup for Auto-Claude with enhanced tools

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  🚀 AUTO-CLAUDE STARTUP - Enhanced Tools Edition" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Docker is running
Write-Host "🐳 Step 1: Checking Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Docker is not running!" -ForegroundColor Red
        Write-Host "   Please start Docker Desktop and try again." -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ Docker is running: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker not found! Please install Docker Desktop." -ForegroundColor Red
    exit 1
}

# Step 2: Start FalkorDB
Write-Host ""
Write-Host "🗄️  Step 2: Starting FalkorDB (Memory Layer)..." -ForegroundColor Yellow

# Check if FalkorDB is already running
$falkorRunning = docker ps --filter "name=auto-claude-falkordb" --filter "status=running" -q
if ($falkorRunning) {
    Write-Host "✓ FalkorDB is already running" -ForegroundColor Green
} else {
    Write-Host "   Starting FalkorDB container..." -ForegroundColor Gray
    docker-compose up -d falkordb 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ FalkorDB started successfully" -ForegroundColor Green
    } else {
        Write-Host "⚠️  FalkorDB start had warnings (might already be running)" -ForegroundColor Yellow
    }
}

# Step 3: Verify API keys
Write-Host ""
Write-Host "🔑 Step 3: Checking API keys..." -ForegroundColor Yellow

$envFile = Join-Path $PSScriptRoot ".env"
if (Test-Path $envFile) {
    $envContent = Get-Content $envFile -Encoding UTF8
    $morphKey = $envContent | Select-String "^MORPH_API_KEY=" | Select-Object -First 1
    $azureKey = $envContent | Select-String "^ANTHROPIC_FOUNDRY_API_KEY=" | Select-Object -First 1
    
    if ($morphKey -and $morphKey -notmatch "your_") {
        Write-Host "✓ Morph API key configured" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Morph API key not configured" -ForegroundColor Yellow
    }
    
    if ($azureKey -and $azureKey -notmatch "your_") {
        Write-Host "✓ Azure Foundry API key configured" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Azure Foundry API key not configured" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  .env file not found" -ForegroundColor Yellow
}

# Step 4: Start Auto-Claude UI
Write-Host ""
Write-Host "🎨 Step 4: Starting Auto-Claude UI..." -ForegroundColor Yellow
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  ✨ AUTO-CLAUDE IS STARTING..." -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📌 What to expect:" -ForegroundColor Cyan
Write-Host "   • Vite dev server will start on http://localhost:5173" -ForegroundColor Gray
Write-Host "   • Electron app window will open automatically" -ForegroundColor Gray
Write-Host "   • Python dependencies will be installed (first time)" -ForegroundColor Gray
Write-Host "   • Enhanced tools will load (Morph + Azure Foundry)" -ForegroundColor Gray
Write-Host ""
Write-Host "🛑 To stop: Press Ctrl+C" -ForegroundColor Yellow
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Change to UI directory and start
Set-Location (Join-Path $PSScriptRoot "auto-claude-ui")
npm run dev
