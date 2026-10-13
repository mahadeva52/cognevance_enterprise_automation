# Enterprise Automation & Data Processing System

## Objective
An advanced Python platform that combines file/data processing, external API integration, multithreading, scheduling, SQLite reporting, monitoring dashboard and automated notifications.

## Install
```bash
pip install -r requirements.txt
```

## Run
```bash
python main.py
```

## Dashboard
Choose option 5, then open:
`http://127.0.0.1:5000`

## Scheduler
```bash
python scheduler.py
```
The default scheduler runs the automation workflow daily at 18:00. Change the time in `scheduler.py` if needed.

## Features
- CSV automation
- ThreadPoolExecutor for parallel processing
- External REST API integration
- SQLite database
- JSON automated reports
- Logging and exception handling
- Flask monitoring dashboard
- Local notification output
- Scheduling support

## Repository
`cognevance_enterprise_automation_data_processing`
