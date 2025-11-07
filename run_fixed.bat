@echo off
rem run_fixed.bat - versão robusta do run.bat sem delayed expansion
set "SCRIPT_DIR=%~dp0"
set "PY_EXEC="

rem Se houver um venv local, prefira este python
if exist "%SCRIPT_DIR%.venv\Scripts\python.exe" (
    set "PY_EXEC=%SCRIPT_DIR%.venv\Scripts\python.exe"
) else (
    rem Verificar se existe python no PATH
    where python >nul 2>&1
    if errorlevel 1 (
        echo Python nao encontrado. Instale Python 3.8+ e assegure que 'python' esteja no PATH.
        echo Voce tambem pode criar um virtualenv local com: python -m venv .venv
        pause
        exit /b 1
    ) else (
        set "PY_EXEC=python"
    )
)

rem Se não houver argumentos, abrir a GUI avançada
if "%~1"=="" (
    echo Abrindo GUI avançada (main_enhanced.py)...
    "%PY_EXEC%" "%SCRIPT_DIR%main_enhanced.py"
    set "RC=%ERRORLEVEL%"
    if not "%RC%"=="0" (
        echo Erro ao executar GUI (codigo de saida: %RC%).
    )
    pause
    exit /b %RC%
)

rem Se houver argumentos, encaminhar para o modo CLI (main_cli.py)
echo Executando em modo CLI: %*
"%PY_EXEC%" "%SCRIPT_DIR%main_cli.py" %*
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" (
    echo Erro ao executar CLI (codigo de saida: %RC%).
)
pause
