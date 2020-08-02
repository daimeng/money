#!/bin/bash
docker-compose exec db psql -U app_user -d bank -c 'TRUNCATE exchange, account RESTART IDENTITY CASCADE'
docker-compose exec app flask load-state
docker-compose exec atm pytest -vv
docker-compose exec atm pytest ./tests/run_e2e.py
