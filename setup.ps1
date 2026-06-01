# Initialize Teraka backend project
# Creates necessary directories and templates
# Usage: .\setup.ps1

Write-Host "🔧 Initializing Teraka Backend Project..." -ForegroundColor Green

# Create necessary directories
$dirs = @('logs', 'media', 'staticfiles', 'config')
foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -Type Directory -Force -Path $dir | Out-Null
    }
}
Write-Host "✓ Created directories: $(($dirs) -join ', ')" -ForegroundColor Green

# Copy .env.example to .env if it doesn't exist
if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
    Write-Host "✓ Created .env from template" -ForegroundColor Green
    Write-Host "  ⚠️  WARNING: Edit .env with your configuration before deploying!" -ForegroundColor Yellow
} else {
    Write-Host "✓ .env already exists (skipped copy)" -ForegroundColor Green
}

# Create plugin_config.json.example if needed
$pluginConfigPath = "config\plugin_config.json"
if (-not (Test-Path $pluginConfigPath)) {
    $pluginConfigTemplate = @{
        "api" = @{
            "django_url" = "http://localhost:8000"
            "postgrest_url" = "http://localhost:3000"
            "timeout_seconds" = 30
        }
        "features" = @{
            "enable_offline_mode" = $false
            "auto_sync_interval_minutes" = 60
        }
    } | ConvertTo-Json -Depth 10
    
    Set-Content -Path $pluginConfigPath -Value $pluginConfigTemplate
    Write-Host "✓ Created config/plugin_config.json template" -ForegroundColor Green
}

Write-Host ""
Write-Host "✅ Project initialized successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "   1. Edit .env with your environment-specific settings"
Write-Host "   2. Edit config/plugin_config.json if needed"
Write-Host "   3. Run: docker compose -f docker-compose.prod.yml up --build"
Write-Host ""
Write-Host "📖 For more information:" -ForegroundColor Cyan
Write-Host "   - Documentation: see README.md"
Write-Host "   - Environment variables: see ENVIRONMENT_VARIABLES.md"
Write-Host "   - Backend paths: see BACKEND_PATH_ISSUES.md"
Write-Host ""
