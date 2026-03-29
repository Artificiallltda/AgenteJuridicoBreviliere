#!/bin/bash

echo "========================================="
echo "🚀 Iniciando Agente Jurídico Breviliere"
echo "========================================="
echo ""
echo "⏳ Aguardando 5 segundos antes de iniciar..."
sleep 5
echo ""
echo "📁 Diretório atual: $(pwd)"
echo "📁 Listando diretórios:"
ls -la /app/
echo ""
echo "📁 Verificando data:"
ls -la /app/data/ 2>/dev/null || echo "⚠️ /app/data não existe"
echo ""
echo "📁 Verificando src:"
ls -la /app/src/ 2>/dev/null || echo "⚠️ /app/src não existe"
echo ""
echo "🔧 PYTHONPATH: $PYTHONPATH"
echo "🔧 CHROMA_PERSIST_DIR: $CHROMA_PERSIST_DIR"
echo "🔧 PORT: $PORT"
echo ""

# Adiciona /app ao PYTHONPATH para encontrar os módulos
export PYTHONPATH="/app:${PYTHONPATH:-}"
echo "🔧 PYTHONPATH atualizado: $PYTHONPATH"
echo ""

echo "🚀 Iniciando servidor na porta $PORT..."
echo "========================================="

# Usa python -m para garantir que o caminho esteja correto
cd /app && python -m uvicorn src.main:app --host 0.0.0.0 --port $PORT
