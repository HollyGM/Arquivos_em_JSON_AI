@echo off
setlocal

rem Configurar ambiente
set "SCRIPT_DIR=%~dp0"
set "VENV_DIR=%SCRIPT_DIR%.venv"
set "VENV_PYTHON=%VENV_DIR%\Scripts\python.exe"
set "POPPLER_PATH=%SCRIPT_DIR%dependencies\poppler-23.08.0-0\poppler-23.08.0\Library\bin"

rem Checar ambiente Python
if exist "%VENV_PYTHON%" (
    set "PYTHON=%VENV_PYTHON%"
) else (
    where python >nul 2>&1
    if errorlevel 1 (
        echo [ERRO] Python nao encontrado no sistema.
        echo 1. Instale Python 3.8 ou superior
        echo 2. Assegure que Python esta no PATH
        echo 3. Opcional: Crie um ambiente virtual com 'python -m venv .venv'
        pause
        exit /b 1
    )
    set "PYTHON=python"
)

rem Configurar PATH para Poppler
if exist "%POPPLER_PATH%" (
    set "PATH=%POPPLER_PATH%;%PATH%"
    echo [INFO] Poppler configurado: %POPPLER_PATH%
) else (
    echo [AVISO] Poppler nao encontrado em %POPPLER_PATH%
    echo         OCR em PDFs pode nao funcionar corretamente
)

rem Verificar/instalar dependências
if not exist "%SCRIPT_DIR%requirements.txt" (
    echo [ERRO] requirements.txt nao encontrado
    pause
    exit /b 1
)

echo [INFO] Verificando dependencias...
"%PYTHON%" -m pip install -r "%SCRIPT_DIR%requirements.txt"

rem Executar programa
echo [INFO] Iniciando aplicacao...
if "%~1"=="" (
    echo [INFO] Modo GUI
    start "Conversor PDF/JSON" /wait "%PYTHON%" "%SCRIPT_DIR%main_enhanced.py"
) else (
    echo [INFO] Modo CLI: %*
    "%PYTHON%" "%SCRIPT_DIR%main_cli.py" %*
)

if errorlevel 1 (
    echo [ERRO] A aplicacao encontrou um erro
    pause
    exit /b 1
)

echo [INFO] Execucao concluida com sucesso
pause
exit /b 0