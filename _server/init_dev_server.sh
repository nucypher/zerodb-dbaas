#!/bin/bash

SERVER_CERT=$(python -c 'from ZEO.tests.testssl import server_cert; print(server_cert)')
SERVER_KEY=$(python -c 'from ZEO.tests.testssl import server_key; print(server_key)')

zerodb-manage init_db \
    --username=root \
    --passphrase=123 \
    --server-key=$SERVER_KEY \
    --server-certificate=$SERVER_CERT \
    --user-certificate="" \
    --sock=localhost:8001
