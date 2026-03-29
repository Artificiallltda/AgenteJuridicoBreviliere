#!/bin/bash

echo "========================================="
echo "🚀 Iniciando Agente Jurídico Breviliere"
echo "========================================="
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
echo "🚀 Iniciando servidor na porta $PORT..."
echo "========================================="

uvicorn src.main:app --host 0.0.0.0 --port $PORT
