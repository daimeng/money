#!/bin/bash
./clear-state.sh
wait
./bootstrap.sh
wait
docker-compose exec atm pytest ./tests/run_e2e.py
