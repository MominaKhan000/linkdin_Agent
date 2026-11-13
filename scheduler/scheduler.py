# scheduler/scheduler.py
import schedule
import time
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from ai_engine.post_generator import generate_post

def scheduled_job():
    print("\n⏰ Running scheduled post generation...")
    post = generate_post("LinkedIn AI Marketing Agent - Daily Post")
    if post:
        print(f"✅ Post generated:\n{post[:200]}...")
        # Save to file
        with open("log/scheduled_post.txt", "w") as f:
            f.write(post)

# Schedule daily at 9 AM
schedule.every().day.at("09:00").do(scheduled_job)

print("🕒 Scheduler started. Will run daily at 9:00 AM")
print("Press Ctrl+C to stop")

while True:
    schedule.run_pending()
    time.sleep(60)