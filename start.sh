#!/bin/bash
cd /home/$USER/taskmanageraibot/
docker-compose rm taskbot
git pull
docker build -t ghcr.io/igamingsolutions/tgbot:latest -f ./Dockerfile .
docker-compose up taskbot