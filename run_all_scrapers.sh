#!/bin/bash

cd /home/bitech-office/Sanwal/football_app

echo "----- RUN START $(date) -----" >> logs/cron.log

# Activate venv and run scripts
/home/bitech-office/Sanwal/football_app/venv/bin/python app/scrapers/news_url_collector.py >> logs/cron.log 2>&1
/home/bitech-office/Sanwal/football_app/venv/bin/python app/scrapers/news_details.py >> logs/cron.log 2>&1
/home/bitech-office/Sanwal/football_app/venv/bin/python app/scrapers/video_scraper.py >> logs/cron.log 2>&1

echo "----- RUN END $(date) -----" >> logs/cron.log
chmod +x run_all_scrapers.sh
crontab -e

