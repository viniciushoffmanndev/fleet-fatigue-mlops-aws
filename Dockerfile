# 1. Imagem Base: Usamos uma versão enxuta (slim) do Python 3.11 para manter o contêiner leve e rápido
FROM python:3.11-slim

# 2. Variáveis de Ambiente do Sistema: Otimizações para o Python rodar melhor em contêineres
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# 3. Diretório de Trabalho: Cria a pasta /app dentro do Linux e avisa que tudo será feito lá
WORKDIR /app

# 4. Camada de Dependências: Copia APENAS o requirements primeiro. 
# Isso usa o cache do Docker e acelera builds futuros se você não mudar as bibliotecas.
COPY requirements.txt .

# 5. Instalação: Rodamos o pip install sem guardar o cache do pip (deixa a imagem menor)
RUN pip install --no-cache-dir -r requirements.txt

# 6. Camada de Código: Agora sim, copiamos todo o nosso código (a pasta src) para dentro do contêiner
COPY src/ ./src/

# 7. Porta de Rede: Sinaliza que o contêiner vai escutar na porta 8000
EXPOSE 8000

# 8. O Motor de Ignição: O comando que será executado assim que o contêiner ligar na AWS
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]