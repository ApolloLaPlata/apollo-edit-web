FROM python:3.10-slim

# O Hugging Face Spaces exige que rodemos como um usuario nao-root (ID 1000)
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

# Define o diretorio de trabalho
WORKDIR /app

# Instala as dependencias do backend
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia todo o codigo do backend (Apollo Edit Backend Pilar 3)
COPY --chown=user . .

# O Hugging Face exige que a aplicacao escute na porta 7860
EXPOSE 7860

# Inicia o servidor FastAPI do Apollo Edit Web
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
