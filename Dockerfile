FROM python:3.12-slim

WORKDIR /app

# Instala dependencias do sistema necessarias para weasyprint e outras libs
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libpango-1.0-0 \
    libharfbuzz0b \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Cria diretórios de dados
RUN mkdir -p /app/data/chroma /app/data/outputs /app/src/documents/templates

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código fonte (incluindo start.sh)
COPY . .

# Garante que start.sh seja executável
RUN chmod +x start.sh

# Configura PYTHONPATH para encontrar os módulos
ENV PYTHONPATH=/app

# Variáveis de ambiente padrão
ENV CHROMA_PERSIST_DIR=/app/data/chroma
ENV DATA_OUTPUT_DIR=/app/data/outputs

EXPOSE 8000

# Usa o start.sh que configura PYTHONPATH dinamicamente
CMD ["bash", "start.sh"]
