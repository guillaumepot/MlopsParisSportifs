#!/bin/bash

# Update & upgrade all packages
sudo apt update && sudo apt upgrade -y

# Upgrade Docker version to latest
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do sudo apt-get remove $pkg; done
sudo apt-get update

sudo apt-get install ca-certificates curl

sudo install -m 0755 -d /etc/apt/keyrings

sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc

sudo chmod a+r /etc/apt/keyrings/docker.asc

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update

sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Check docker-compose version, upgrade if version < 2.14 (et forcera l'update si la version n'est pas à jour)
  # V2.14 is minimal requirement for running airflow
docker-compose --version | \
awk '{print $3}' | \
cut -d ',' -f1 | \
{ read version; \
  if [ "$(printf '%s\n' "2.14" "$version" | sort -V | head -n1)" = "$version" ]; then \
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && \
    sudo chmod +x /usr/local/bin/docker-compose; \
  fi; \
}

# Add bash link to docker-compose
sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

# Check docker-compose version
docker-compose --version