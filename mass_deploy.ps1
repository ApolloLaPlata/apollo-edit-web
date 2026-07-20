$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$dbPath = "E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\cloud_tools\cloud_accounts_db.json"
$accounts = Get-Content $dbPath -Raw | ConvertFrom-Json

Write-Host "Iniciando Deploy em Massa (MOSS-TTS 25GB)..." -ForegroundColor Cyan
Write-Host "A PRIMEIRA conta pode demorar para baixar os 25GB. As outras aproveitarão o cache da Modal e terminarão em segundos.`n" -ForegroundColor Yellow

foreach ($acc in $accounts) {
    if (-not [string]::IsNullOrEmpty($acc.token_id) -and -not [string]::IsNullOrEmpty($acc.token_secret)) {
        Write-Host "==========================================" -ForegroundColor Green
        Write-Host "Realizando Deploy na Conta: $($acc.nome_conta)" -ForegroundColor Green
        Write-Host "==========================================" -ForegroundColor Green
        
        $env:MODAL_TOKEN_ID = $acc.token_id
        $env:MODAL_TOKEN_SECRET = $acc.token_secret
        $env:PYTHONIOENCODING = "utf-8"
        
        # Executa o deploy do Router Web (Wan, MOSS, LTX, Flux)
        modal deploy -m backend.cloud_tools.apollo_modal_engine
        
        # Executa o deploy do Painel Web Applio RVC (Treinamento)
        modal deploy -m backend.cloud_tools.engines.applio_engine
        
        Write-Host "Deploy da conta $($acc.nome_conta) concluído!`n" -ForegroundColor Green
    } else {
        Write-Host "Conta $($acc.nome_conta) ignorada (Faltam credenciais Modal)." -ForegroundColor Red
    }
}

Write-Host "🎉 Deploy em Massa Finalizado!" -ForegroundColor Cyan
