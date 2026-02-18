import schedule
import time

def daily_task():
    print("Daily task is running...")  # Replace with your task

# Schedule the task to run daily at a specific time
schedule.every().day.at("10:00").do(daily_task)  # Schedule for 10:00 AM

while True:
    schedule.run_pending()
    time.sleep(60)  # Wait one minute before checking again