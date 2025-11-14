@echo off
rem ============================================================
rem  Launcher simplificado para GUI - Mantém console visível
rem ============================================================

set "SCRIPT_DIR=%~dp0"

rem Detectar Python
if exist "%SCRIPT_DIR%.venv\Scripts\python.exe" (
    set "PYTHON=%SCRIPT_DIR%.venv\Scripts\python.exe"
) else (
    set "PYTHON=python"
)

rem Executar GUI diretamente
"%PYTHON%" "%SCRIPT_DIR%main_enhanced.py"

rem Pausa apenas se houver erro
if errorlevel 1 (
    echo.
    echo [ERRO] A aplicacao encontrou um erro.
    echo Verifique gui_debug.log para detalhes.
    pause
)
