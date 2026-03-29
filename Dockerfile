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

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código fonte completo
COPY src/ ./src/

# Copia start.sh
COPY start.sh .
RUN chmod +x start.sh

# Configura PYTHONPATH para encontrar os módulos
ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["bash", "start.sh"]
