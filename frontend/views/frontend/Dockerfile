FROM python:3.9-slim

# Evita arquivos .pyc e garante logs imediatos
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação e a pasta de views
COPY . .

# Expõe a porta padrão do Streamlit
EXPOSE 8501

# Comando de inicialização apontando para o novo main.py
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]