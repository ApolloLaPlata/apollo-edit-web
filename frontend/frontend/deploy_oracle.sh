#!/bin/bash
# ==========================================
# SCRIPT DE DEPLOY ORACLE CLOUD (AUTO-BLOG CMS)
# ==========================================
# Este script instala Node.js, PM2, Nginx e sobe o servidor.
# Execute no seu servidor Ubuntu como ROOT.

echo "🔥 Iniciando Protocolo de Voo (Deploy Oracle) 🔥"

# 1. Atualizar Pacotes
echo "➡️ Atualizando repositórios..."
sudo apt update && sudo apt upgrade -y

# 2. Instalar Node.js 20.x
echo "➡️ Instalando Node.js 20..."
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# 3. Instalar PM2 Global
echo "➡️ Instalando PM2..."
sudo npm install -g pm2

# 4. Instalar Nginx
echo "➡️ Instalando Nginx Firewall..."
sudo apt install nginx -y

# 5. Build do Next.js
echo "➡️ Instalando pacotes do projeto e gerando a Build..."
# Supõe que o script está sendo rodado dentro da pasta 'frontend'
npm install
npm run build

# 6. Ativar Daemon e Web Server
echo "➡️ Iniciando Motores (PM2)..."
pm2 start npm --name "apollo-web" -- start
pm2 start daemon.js --name "apollo-daemon"
pm2 save
pm2 startup

echo "✅ DEPLOY CONCLUÍDO! O sistema base está rodando na porta 3000 em Background!"
echo "➡️ Siga as instruções do arquivo 'nginx_multi_domain.conf' para expor o servidor ao público usando seus domínios."
