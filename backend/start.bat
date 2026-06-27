@echo off
echo ====================================
echo   CxIA Backend - Iniciando...
echo ====================================
echo.

cd /d %~dp0

echo Verificando dependencias...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ERRO: Falha ao instalar dependencias
    pause
    exit /b 1
)

echo.
echo Iniciando servidor na porta 8000...
echo.
echo URLs uteis:
echo   - API: http://localhost:8000
echo   - Docs: http://localhost:8000/docs
echo   - Health: http://localhost:8000/health
echo.
echo Pressione Ctrl+C para parar o servidor
echo.

python main.py

pause
