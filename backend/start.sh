#!/bin/bash

echo "===================================="
echo "  CxIA Backend - Iniciando..."
echo "===================================="
echo ""

cd "$(dirname "$0")"

echo "Verificando dependências..."
pip install -r requirements.txt --quiet
if [ $? -ne 0 ]; then
    echo "ERRO: Falha ao instalar dependências"
    exit 1
fi

echo ""
echo "Iniciando servidor na porta 8000..."
echo ""
echo "URLs úteis:"
echo "  - API: http://localhost:8000"
echo "  - Docs: http://localhost:8000/docs"
echo "  - Health: http://localhost:8000/health"
echo ""
echo "Pressione Ctrl+C para parar o servidor"
echo ""

python main.py
