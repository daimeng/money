#!/bin/bash
docker-compose exec app pytest -v $@
docker-compose exec atm pytest -v $@
