# Usamos a versão estável atual
FROM python:3.9-slim-bookworm

# Evita arquivos .pyc e garante logs em tempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# --- CONFIGURAÇÃO DE REDE E MIRRORS BRASILEIROS ---
RUN sed -i 's/deb.debian.org/ftp.br.debian.org/g' /etc/apt/sources.list.d/debian.sources || \
    sed -i 's/deb.debian.org/ftp.br.debian.org/g' /etc/apt/sources.list && \
    echo 'Acquire::ForceIPv4 "true";' > /etc/apt/apt.conf.d/99force-ipv4

# Instala dependências do sistema
RUN apt-get clean && apt-get update --fix-missing && \
    apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    libaio1 \
    unzip \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# --- INSTALAÇÃO DO ORACLE INSTANT CLIENT (MODO OFFLINE) ---
WORKDIR /opt/oracle

# COPIAMOS o arquivo que você baixou manualmente para dentro do container
COPY instantclient-basic-linux.x64-19.22.0.0.0dbru.zip .

# Descompactamos e limpamos
RUN unzip instantclient-basic-linux.x64-19.22.0.0.0dbru.zip && \
    rm -f instantclient-basic-linux.x64-19.22.0.0.0dbru.zip

# Define variáveis de ambiente para o Oracle Thick Mode
ENV LD_LIBRARY_PATH=/opt/oracle/instantclient_19_22

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000