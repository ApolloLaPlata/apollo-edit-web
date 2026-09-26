# Usar imagem oficial do Node.js (Alpine para menor tamanho)
FROM node:18-alpine

# Instalar dependências pesadas do sistema (FFMPEG para os vídeos, e dependências de build para sqlite3)
RUN apk add --no-cache ffmpeg python3 make g++ 

WORKDIR /app

# Copiar arquivos de pacote
COPY package.json package-lock.json* ./

# Instalar pacotes NPM (incluindo PM2 globalmente para gerenciar workers)
RUN npm ci
RUN npm install -g pm2

# Copiar todo o código
COPY . .

# Fazer o Build do Next.js
ENV NEXT_TELEMETRY_DISABLED 1
RUN npm run build

# O docker-compose mapeará volumes reais para as pastas abaixo
# RUN mkdir -p public/uploads public/exports

# Expor porta
EXPOSE 3000

# Usamos o ecosystem.config.js do PM2 para subir o Next.js e o daemon.js juntos
CMD ["pm2-runtime", "start", "ecosystem.config.js"]
