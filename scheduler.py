import time
import schedule
from main import scheduled_job

# Change the schedule below if required.
schedule.every().day.at("18:00").do(scheduled_job)

print("Scheduler started. Daily job is configured for 18:00.")
while True:
    schedule.run_pending()
    time.sleep(30)
