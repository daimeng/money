#!/bin/bash
docker-compose exec app flask load-state
docker-compose exec atm python load_money.py 10000
