#!/bin/bash
cd /home/$USER/taskbot/
docker-compose rm taskbot
git pull
docker build -t ghcr.io/igamingsolutions/taskbot:latest -f ./Dockerfile .
docker-compose up taskbot