# Script PowerShell pour lancer Django et PostgREST en même temps
# À exécuter depuis le répertoire backend_django

Write-Host "🚀 Démarrage des serveurs Teraka..." -ForegroundColor Green
Write-Host ""

# Vérifier que nous sommes dans le bon répertoire
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Démarrer PostgREST en arrière-plan
Write-Host "▶️  Lancement de PostgREST (port 3000)..." -ForegroundColor Cyan
$postgrestPath = ".\api\postgrest.exe"
$postgrestConfig = ".\api\postgrest.conf"

if (-Not (Test-Path $postgrestPath)) {
    Write-Host "❌ Erreur: postgrest.exe non trouvé à $postgrestPath" -ForegroundColor Red
    exit 1
}

if (-Not (Test-Path $postgrestConfig)) {
    Write-Host "❌ Erreur: postgrest.conf non trouvé à $postgrestConfig" -ForegroundColor Red
    exit 1
}

# Lancer PostgREST
$postgrestProcess = Start-Process -FilePath $postgrestPath `
    -ArgumentList "-c", $postgrestConfig `
    -WorkingDirectory ".\api" `
    -PassThru `
    -NoNewWindow

Write-Host "✓ PostgREST lancé (PID: $($postgrestProcess.Id))" -ForegroundColor Green

# Attendre un peu que PostgREST démarre
Start-Sleep -Seconds 2

# Démarrer Django en arrière-plan
Write-Host "▶️  Lancement de Django (port 8000)..." -ForegroundColor Cyan
$pythonExe = (Get-Command python).Source

$djangoProcess = Start-Process -FilePath $pythonExe `
    -ArgumentList "manage.py", "runserver", "0.0.0.0:8000" `
    -PassThru `
    -NoNewWindow

Write-Host "✓ Django lancé (PID: $($djangoProcess.Id))" -ForegroundColor Green

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host "✓ Les deux serveurs sont maintenant en cours d'exécution" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Accès :" -ForegroundColor Yellow
Write-Host "   • Django Admin  : http://localhost:8000/admin/" -ForegroundColor White
Write-Host "   • Login API     : http://localhost:8000/api/login/" -ForegroundColor White
Write-Host "   • PostgREST     : http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "🛑 Pour arrêter les serveurs, pressez Ctrl+C" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host ""

# Attendre que les processus se terminent
Wait-Process -Id $postgrestProcess.Id, $djangoProcess.Id

Write-Host "✓ Les serveurs ont été arrêtés." -ForegroundColor Green
