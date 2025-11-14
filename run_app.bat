@echo off
TITLE Conversor de Documentos para JSON

ECHO --- Ativando ambiente virtual e iniciando a aplicacao ---

REM Define o caminho para o script de ativacao do ambiente virtual
set VENV_ACTIVATE_SCRIPT=%~dp0.venv\Scripts\activate.bat

REM Verifica se o script de ativacao existe
if not exist "%VENV_ACTIVATE_SCRIPT%" (
    ECHO ERRO: O ambiente virtual (.venv) nao foi encontrado.
    ECHO Por favor, execute o script de setup ou crie o ambiente manualmente.
    pause
    exit /b
)

REM Ativa o ambiente virtual do projeto
call "%VENV_ACTIVATE_SCRIPT%"

ECHO --- Ambiente ativado. Executando o programa... ---
python "%~dp0main_enhanced.py"

ECHO.
ECHO --- O programa foi finalizado ou ocorreu um erro. ---
ECHO Pressione qualquer tecla para fechar esta janela.
pause
