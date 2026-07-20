@echo off
cd /d "%~dp0"
title Apollo Studio
echo ========================================
echo    APOLLO STUDIO - MOTOR CENTRAL
echo ========================================
echo.
echo Iniciando o programa...
echo.
echo ========================================
echo Limpando Processos Zumbis do Apollo...
echo ========================================
wmic process where "name='python.exe' and CommandLine like '%backend\\maestro\\main.py%'" call terminate >nul 2>&1
wmic process where "name='python.exe' and CommandLine like '%backend\\router\\load_balancer.py%'" call terminate >nul 2>&1
wmic process where "name='python.exe' and CommandLine like '%servidor_web.py%'" call terminate >nul 2>&1
wmic process where "name='chrome.exe' and CommandLine like '%%.wwebjs_auth%%'" call terminate >nul 2>&1
wmic process where "name='node.exe' and CommandLine like '%%whatsapp_bot%%'" call terminate >nul 2>&1


for /f "tokens=5" %%a in ('netstat -aon ^| find "8080" ^| find "LISTENING"') do taskkill /f /pid %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| find "5001" ^| find "LISTENING"') do taskkill /f /pid %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| find "8000" ^| find "LISTENING"') do taskkill /f /pid %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| find "3000" ^| find "LISTENING"') do taskkill /f /pid %%a >nul 2>&1
echo Concluido. Zumbis eliminados com sucesso.
echo.

REM Verificar se o ambiente virtual existe
if exist "venv\Scripts\python.exe" (
    echo Usando Python do ambiente virtual...
    set PYTHON_CMD=venv\Scripts\python.exe
) else (
    echo AVISO: Ambiente virtual nao encontrado!
    echo Tentando usar Python do sistema...
    set PYTHON_CMD=python
)

REM Verificar se o arquivo principal existe
if not exist "apollo_studio.py" (
    echo ERRO: Arquivo apollo_studio.py nao encontrado!
    echo Certifique-se de que o arquivo esta na mesma pasta deste BAT.
    echo.
    pause
    exit /b 1
)


REM Executar o programa principal
echo.
echo Iniciando Ponte do WhatsApp no mesmo terminal...
start /b cmd /c "start_whatsapp.bat"
echo.
echo Iniciando Cao de Guarda (Load Balancer) no mesmo terminal...
start /b %PYTHON_CMD% backend\router\load_balancer.py
echo.
echo Iniciando Maestro API (Gateway) no mesmo terminal...
start /b %PYTHON_CMD% backend\maestro\main.py
echo.

echo Executando Apollo Studio...
echo.
%PYTHON_CMD% "apollo_studio.py"

REM Verificar se houve erro na execucao
if %errorlevel% neq 0 (
    echo.
    echo ERRO: O programa foi encerrado com erro!
    echo Codigo de erro: %errorlevel%
    echo.
    pause
) else (
    echo.
    echo Programa encerrado com sucesso!
)

REM Manter a janela aberta para ver mensagens
echo.
echo Pressione qualquer tecla para fechar...
pause >nul
