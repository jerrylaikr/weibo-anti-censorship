from weibo_spider.spider import main
from absl import app
import time

SLEEP_TIME = 1200


if __name__ == "__main__":
    while True:
        # reset since_date

        # Run weibo_spider
        try:
            print("Running weibo_spider...")
            app.run(main)
        except Exception as e:
            print("ERROR")

        print(f"Sleeping for {SLEEP_TIME}s...")
        time.sleep(SLEEP_TIME)
