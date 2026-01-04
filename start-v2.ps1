# ============================================================================
# AUTO CLAUDE v2.7.2 - SYNTHIQ ENHANCED STARTUP SCRIPT
# ============================================================================
# Start Auto-Claude with Azure Foundry and Enhanced Tools (Morph + Augment)
# ============================================================================

Write-Host "`n🚀 Starting Auto-Claude v2.7.2 with Enhanced Tools...`n" -ForegroundColor Cyan

# ============================================================================
# Step 1: Check Python 3.12+
# ============================================================================
Write-Host "📦 Checking Python..." -ForegroundColor Yellow

try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python 3\.1[2-9]|Python 3\.[2-9][0-9]") {
        Write-Host "✓ $pythonVersion" -ForegroundColor Green
    } else {
        Write-Host "✗ Python 3.12+ required. Found: $pythonVersion" -ForegroundColor Red
        Write-Host "Install: winget install Python.Python.3.12" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "✗ Python not found" -ForegroundColor Red
    Write-Host "Install: winget install Python.Python.3.12" -ForegroundColor Yellow
    exit 1
}

# ============================================================================
# Step 2: Check .env file
# ============================================================================
Write-Host "`n📝 Checking configuration..." -ForegroundColor Yellow

if (Test-Path "apps\backend\.env") {
    Write-Host "✓ .env file found" -ForegroundColor Green
    
    # Check for required API keys
    $envContent = Get-Content "apps\backend\.env" -Raw
    
    $requiredKeys = @{
        "ANTHROPIC_FOUNDRY_API_KEY" = "Azure Foundry"
        "MORPH_API_KEY" = "Morph LLM"
        "VOYAGE_API_KEY" = "Voyage AI"
    }
    
    $missingKeys = @()
    foreach ($key in $requiredKeys.Keys) {
        if ($envContent -match "$key=([^`n]+)" -and $Matches[1] -ne "your_*_here") {
            Write-Host "  ✓ $($requiredKeys[$key])" -ForegroundColor Green
        } else {
            Write-Host "  ✗ $($requiredKeys[$key])" -ForegroundColor Red
            $missingKeys += $key
        }
    }
    
    if ($missingKeys.Count -gt 0) {
        Write-Host "`n⚠️  Missing API keys. Please add them to apps\backend\.env" -ForegroundColor Yellow
        Write-Host "Continue anyway? (Y/N): " -NoNewline -ForegroundColor Yellow
        $response = Read-Host
        if ($response -ne "Y" -and $response -ne "y") {
            exit 1
        }
    }
} else {
    Write-Host "✗ .env file not found" -ForegroundColor Red
    Write-Host "Copy apps\backend\.env.example to apps\backend\.env and add your API keys" -ForegroundColor Yellow
    exit 1
}

# ============================================================================
# Step 3: Verify Enhanced Tools
# ============================================================================
Write-Host "`n🔧 Checking enhanced tools..." -ForegroundColor Yellow

$tools = @(
    "apps\backend\integrations\morph\client.py",
    "apps\backend\integrations\augment\client.py",
    "apps\backend\integrations\enhanced_tools.py"
)

$allPresent = $true
foreach ($tool in $tools) {
    if (Test-Path $tool) {
        Write-Host "  ✓ $(Split-Path $tool -Leaf)" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $(Split-Path $tool -Leaf)" -ForegroundColor Red
        $allPresent = $false
    }
}

if (-not $allPresent) {
    Write-Host "`n⚠️  Some enhanced tools missing. Run migration script first." -ForegroundColor Yellow
}

# ============================================================================
# Step 4: Start Auto-Claude
# ============================================================================
Write-Host "`n🎯 Starting Auto-Claude v2.7.2...`n" -ForegroundColor Cyan

try {
    # Run in development mode (hot reload)
    npm run dev
} catch {
    Write-Host "`n✗ Failed to start Auto-Claude" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}

# ============================================================================
# USAGE
# ============================================================================
# .\start-v2.ps1
#
# NOTE: v2.7.2 uses LadybugDB (embedded) - no Docker required! 🎉
# ============================================================================
