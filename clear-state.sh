#!/bin/bash
docker-compose exec db psql -U app_user -d bank -c 'TRUNCATE exchange, account RESTART IDENTITY CASCADE'
docker-compose exec atm python dump_money.py
