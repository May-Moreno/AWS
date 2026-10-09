#!/usr/bin/env bash
# Despliegue idempotente. Ejecutar de nuevo tras cada reinicio del laboratorio.
set -euo pipefail
APP_DIR="$(cd "$(dirname "$0")" && pwd)"
RUN_USER="$(whoami)"

echo ">> Instalando dependencias del sistema"
if command -v dnf >/dev/null; then
  sudo dnf install -y python3 python3-pip nginx git nodejs npm
else
  sudo apt-get update -y
  sudo apt-get install -y python3 python3-venv python3-pip nginx git nodejs npm curl
fi

echo ">> Backend"
cd "$APP_DIR/backend"
python3 -m venv .venv
.venv/bin/pip install --quiet -r requirements.txt
if [ ! -f .env ]; then
  ADMIN_PW="$(openssl rand -hex 8)"
  ANALYST_PW="$(openssl rand -hex 8)"
  cat > .env <<ENVEOF
ENV=prod
SECRET_KEY=$(openssl rand -hex 32)
ACCESS_TOKEN_MINUTES=15
ADMIN_PASSWORD=$ADMIN_PW
ANALYST_PASSWORD=$ANALYST_PW
ENVEOF
  chmod 600 .env
  echo "   Usuario admin     -> admin / $ADMIN_PW"
  echo "   Usuario analista  -> analista / $ANALYST_PW"
fi

sudo tee /etc/systemd/system/zt-backend.service >/dev/null <<UNIT
[Unit]
Description=Zero Trust FastAPI
After=network.target
[Service]
User=$RUN_USER
WorkingDirectory=$APP_DIR/backend
EnvironmentFile=$APP_DIR/backend/.env
ExecStart=$APP_DIR/backend/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
NoNewPrivileges=true
PrivateTmp=true
[Install]
WantedBy=multi-user.target
UNIT
sudo systemctl daemon-reload
sudo systemctl enable --now zt-backend
sudo systemctl restart zt-backend

echo ">> Frontend"
cd "$APP_DIR/frontend"
npm install --no-audit --no-fund
npm run build
sudo mkdir -p /var/www/zt-app
sudo rm -rf /var/www/zt-app/*
sudo cp -r dist/* /var/www/zt-app/

echo ">> Nginx"
NGINX_USER=$(id -u nginx >/dev/null 2>&1 && echo nginx || echo www-data)
sed "s/^user nginx;/user $NGINX_USER;/" "$APP_DIR/deploy/nginx.conf" | sudo tee /etc/nginx/nginx.conf >/dev/null
sudo nginx -t
sudo systemctl enable --now nginx
sudo systemctl restart nginx

echo ">> Listo. Abre http://<IP-PUBLICA-DE-LA-EC2> (puerto 80)"
