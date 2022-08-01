from datetime import date, datetime, timedelta
from weibo_spider.spider import Spider, _get_config
from weibo_spider import config_util, datetime_util
import sys
import os
import json
from absl.app import parse_flags_with_usage, _run_init, _init_callbacks
import time
import logging
from wbac.spider_rev import main_rev
import pytz  # TZ CHANGE


REV_INTERVAL = timedelta(minutes=30)
SLEEP_TIME = 600
logger = logging.getLogger("spider")


def remove_unchanged():
    print("removing unchanged weibo...")
    pass


def main(_):
    try:
        config = _get_config()
        config_util.validate_config(config)
        wb = Spider(config)
        wb.start()  # 爬取微博信息
    except Exception as e:
        raise
        sys.exit()


def run(
    main,
    argv=None,
    flags_parser=parse_flags_with_usage,
):
    args = _run_init(
        sys.argv if argv is None else argv,
        flags_parser,
    )
    while _init_callbacks:
        callback = _init_callbacks.popleft()
        callback()
    main(args)


if __name__ == "__main__":
    rev_range_since = datetime.now().astimezone(pytz.timezone("PRC"))  # TZ CHANGE

    # update since_date to time now
    # first fetch will happen after SLEEP_TIME
    config_path = os.getcwd() + os.sep + "config.json"
    with open(config_path) as f:
        config = json.loads(f.read())
    config["since_date"] = rev_range_since.strftime("%Y-%m-%d %H:%M")
    config["end_date"] = "now"
    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)

    # start running
    while True:
        print(f"Sleeping for {SLEEP_TIME}s...")
        time.sleep(SLEEP_TIME)

        # Run weibo_spider
        run(main)

        # If REV_INTERVAL passed since last rev, run rev
        now = datetime.now().astimezone(pytz.timezone("PRC"))  # TZ CHANGE
        rev_range_end = rev_range_since + REV_INTERVAL
        if now > rev_range_end + REV_INTERVAL:
            main_rev(
                rev_range_since.strftime("%Y-%m-%d %H:%M"),
                rev_range_end.strftime("%Y-%m-%d %H:%M"),
            )
            remove_unchanged()
            rev_range_since += REV_INTERVAL
