#!/bin/bash -ex

venv_name="dm-tools-server"

dir=$(dirname $(which virtualenv))

${dir}/virtualenv -p $(which python3) $venv_name
source $venv_name/bin/activate

pip install .

cd api-server

uvicorn --workers 2 --access-log --use-colors --limit-concurrency 10 --backlog 10 --host 0.0.0.0 --port 443 --ssl-keyfile /etc/letsencrypt/live/api.dm-tools.dev/privkey.pem --ssl-certfile /etc/letsencrypt/live/api.dm-tools.dev/fullchain.pem  main:app
