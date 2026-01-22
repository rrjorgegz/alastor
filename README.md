# Alastor
Alastor, Empresa de VC (Calderas) desarrollada por DESOFT VC

## Git
1. [pip install pre-commit, pre-commit install] Solo ejecutar una vez.
2. pre-commit run --all-files

## Estado-del-proyecto
![Badge en Desarollo](https://img.shields.io/badge/STATUS-EN%20DESAROLLO-green)

## Descripción del Proyecto Alastor


## instalar Odoo en proxmox
- Create CT de la plantilla ubuntu-20.04-standard_20.04-1_amd64.tar.gz
- user root y poner la pass 
- apt update
- apt upgrade
- crear usuario odoo (adduser odoo) y añadir a grupo sudo (usermod -aG sudo odoo)
- (apt install wireguard resolvconf curl) y copiar para /etc/wireguard/ la configuracion de wg0.conf que se obtiene de descargar de tu cuenta protonvpn.com 
- habilitar vpn (wg-quick up wg0) y desabilitar (wg-quick down wg0) para activar de forma permanente luego de habilitar vpn ponemos (systemctl enable wg-quick@wg0.service) y desabilitar (systemctl disable wg-quick@wg0.service),
- instalar docker https://docs.docker.com/engine/install/ubuntu/ 
    ```
        apt install ca-certificates curl
        install -m 0755 -d /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
        chmod a+r /etc/apt/keyrings/docker.asc
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        apt update
        apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    ```
- añadir a grupo docker (usermod -aG docker odoo)
- descargar repositorio en /home/odoo (git clone https://github.com/rrjorgegz/hidraulica.git)

## Desplegar 
docker compose -f 'docker-compose.yaml' up -d --build'

## Desplegar Odoo en [Coolify](https://coolify.io) o [Dokploy](https://dokploy.com) con CI/DI

## Autores
| [<img src="https://avatars.githubusercontent.com/u/101665649?v=4" width=115><br><sub>rrjorgegz</sub>](https://github.com/rrjorgegz) |
| :---: |
