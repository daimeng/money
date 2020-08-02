#!/bin/bash
docker-compose exec app pytest $@
docker-compose exec atm pytest $@
