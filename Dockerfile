# 1. Imagem base do Python
FROM python:3.11-slim

# 2. Impedir que o Python grave arquivos .pyc e forçar o log direto no terminal
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 3. Definir o diretório de trabalho dentro do container
WORKDIR /app

# 4. Copiar os requisitos primeiro
COPY requirements.txt .

# 5. Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copiar o restante do código da API
COPY . .

# 7. Expor a porta que o FastAPI vai rodar
EXPOSE 8000

# 8. Comando para iniciar o servidor uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]