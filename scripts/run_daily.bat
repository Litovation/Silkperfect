@echo off
rem Once-a-day job for Windows Task Scheduler: new NSE prices and the pretend account.
cd /d "%~dp0.."
python -m silkperfect daily >> data\daily.log 2>&1
