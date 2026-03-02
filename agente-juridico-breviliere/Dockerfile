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

# Copia apenas o necessario para manter a imagem limpa
COPY src/ src/
COPY knowledge_base/ knowledge_base/

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
