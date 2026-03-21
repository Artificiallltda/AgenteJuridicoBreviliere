#!/bin/bash
PORT=${PORT:-8000}
echo "Iniciando servidor na porta $PORT..."
uvicorn src.main:app --host 0.0.0.0 --port $PORT
