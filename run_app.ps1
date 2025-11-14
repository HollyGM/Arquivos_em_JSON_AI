# Script PowerShell para executar o Conversor de Documentos para JSON
$Host.UI.RawUI.WindowTitle = "Conversor de Documentos para JSON"

Write-Host "--- Ativando ambiente virtual e iniciando a aplicacao ---" -ForegroundColor Cyan

# Define o caminho para o script de ativação do ambiente virtual
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvActivateScript = Join-Path $scriptPath ".venv\Scripts\Activate.ps1"

# Verifica se o script de ativação existe
if (-not (Test-Path $venvActivateScript)) {
    Write-Host "ERRO: O ambiente virtual (.venv) nao foi encontrado." -ForegroundColor Red
    Write-Host "Por favor, execute o script de setup ou crie o ambiente manualmente." -ForegroundColor Red
    Read-Host "Pressione ENTER para sair"
    exit
}

# Ativa o ambiente virtual do projeto
& $venvActivateScript

Write-Host "--- Ambiente ativado. Executando o programa... ---" -ForegroundColor Green

# Executa o programa Python
$mainScript = Join-Path $scriptPath "main_enhanced.py"
python $mainScript

Write-Host ""
Write-Host "--- O programa foi finalizado. ---" -ForegroundColor Yellow
Read-Host "Pressione ENTER para fechar esta janela"
