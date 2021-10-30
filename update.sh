#!/bin/bash
git stash
git pull --rebase
git stash pop
python TelegramSavedMessageBot.py