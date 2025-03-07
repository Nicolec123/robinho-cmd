@echo off
echo Iniciando o Robo...
cd /d "%~dp0"  

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python não encontrado! Verifique se o Python está instalado e no PATH.
    exit /b
)

python "%~dp0main.py"  # Força o caminho absoluto para o arquivo main.py
exit
