@echo off
REM FinCA AI - Automated News Fetcher Batch Script
REM This script can be scheduled to run periodically using Windows Task Scheduler

cd /d "%~dp0.."
python scripts\automated_news_fetcher.py

REM Exit with the same code as the Python script
exit /b %errorlevel%