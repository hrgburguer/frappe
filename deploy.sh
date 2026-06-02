#!/bin/bash

echo "----------------------------"
echo "-- Atualizando o ambiente --"
echo "----------------------------"
apt update -y
apt install -y curl nano jq git zip unzip

echo "-------------------------"
echo "-- Instalando o docker --"
echo "-------------------------"
curl -fsSL https://get.docker.com/ | bash

echo "--------------------------------"
echo "-- Instalado o docker compose --"
echo "--------------------------------"
curl -L "https://github.com/docker/compose/releases/download/1.26.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

echo "---------------------------"
echo "-- Logando no Docker Hub --"
echo "---------------------------"
echo $DOCKER_PASSWORD | docker login --username $DOCKER_USERNAME --password-stdin

echo "------------------------"
echo "-- Instalando AWS CLI --"
echo "------------------------"
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip -o awscliv2.zip
sudo ./aws/install --update
rm -rf awscliv2 awscliv2.zip

echo "-----------------------"
echo "-- Configurando .env --"
echo "-----------------------"
bash /app/scripts/env.sh

echo "---------------------------"
echo "-- Buildando os serviços --"
echo "---------------------------"
docker-compose -f docker-compose.production.yaml build --no-cache

echo "------------------------"
echo "-- Iniciando serviços --"
echo "------------------------"
docker-compose -f docker-compose.production.yaml up -d

sleep 30

echo "-----------------------------"
echo "-- Configurando Cloudflare --"
echo "-----------------------------"
bash /app/scripts/cloudflare.sh