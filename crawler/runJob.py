import schedule
import time
from crawler_bonbanh import main  # replace with your actual import


def job():
    main()


if __name__ == "__main__":
    schedule.every(10).seconds.do(job)
    while True:
        # Run pending jobs
        schedule.run_pending()
        time.sleep(1)
