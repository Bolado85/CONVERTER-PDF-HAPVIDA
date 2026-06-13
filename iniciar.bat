@echo off
title Hapvida +Odonto - Rede Credenciada
color 1F
cls

echo.
echo  =====================================================
echo   HAPVIDA +ODONTO - Rede Credenciada
echo   Iniciando o sistema com Alta Performance...
echo  =====================================================
echo.

:: Ir para a pasta onde o .bat esta
cd /d "%~dp0"

:: Verificar se Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
echo  [ERRO] Python nao encontrado!
echo.
echo  Instale o Python em: https://www.python.org/downloads/
echo  Marque a opcao "Add Python to PATH" durante a instalacao.
echo.
pause
exit /b
)

:: Instalar dependencias pelo requirements.txt
echo  [1/2] Verificando dependencias essenciais...
python -m pip install -r requirements.txt

echo.
echo  [2/2] Abrindo o navegador e iniciando servidor...
echo  Para encerrar, feche esta janela ou pressione Ctrl+C
echo.

:: Inicia o Streamlit
python -m streamlit run app.py --server.port 8501 --browser.gatherUsageStats false

if errorlevel 1 (
echo.
echo  =====================================================
echo   [ERRO] O sistema fechou inesperadamente.
echo   Verifique as mensagens de erro acima.
echo  =====================================================
echo.
pause
)