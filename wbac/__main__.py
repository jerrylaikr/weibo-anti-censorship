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
from pymongo import MongoClient
import pytz  # TZ CHANGE


REV_INTERVAL = timedelta(hours=12)
SLEEP_TIME = 60 * 10  # in seconds
logger = logging.getLogger("spider")


def remove_unchanged(connection_string):
    """
    移除两个collections的交集
    算法有待优化
    """
    logger.info("removing unchanged weibo...")
    client = MongoClient(connection_string)
    db = client["weibo"]
    coll_wb, coll_rev = db["weibo"], db["weibo_rev"]
    weibo_rev_list = []

    # get all documents from weibo_rev collection
    for doc_rev in coll_rev.find(
        {}, {"_id": 1, "id": 1, "content": 1}, sort=[("publish_time", 1)]
    ):
        weibo_rev_list.append(doc_rev)

    # for each document in weibo_rev collection
    # if the document in weibo collection with the same id
    # has identical content (i.e. exists and is not modified)
    # remove such document from both collection
    del_count = 0
    for doc_rev in weibo_rev_list:
        doc_wb = coll_wb.find_one({"id": doc_rev["id"]}, {"_id": 1, "content": 1})
        if doc_wb and doc_wb["content"] == doc_rev["content"]:
            del_count += 1
            logger.info(f"delete doc with id = \"{doc_rev['id']}'\" from weibo coll")
            coll_wb.delete_one({"_id": doc_wb["_id"]})
        coll_rev.delete_one({"_id": doc_rev["_id"]})

    # log deletion report
    logger.info(f"{del_count}/{len(weibo_rev_list)} deleted from weibo coll")


def main(_):
    try:
        config = _get_config()
        config_util.validate_config(config)
        wb = Spider(config)
        wb.start()  # 爬取微博信息
    except Exception as e:
        raise


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
    logger.info('Updating "since_date" to: {}'.format(config["since_date"]))
    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)

    # start running
    while True:
        logger.info(f"Sleeping for {SLEEP_TIME}s...")
        time.sleep(SLEEP_TIME)

        # If REV_INTERVAL passed since last rev, run spider_rev
        now = datetime.now().astimezone(pytz.timezone("PRC"))  # TZ CHANGE
        rev_range_end = rev_range_since + REV_INTERVAL
        if now > rev_range_end + REV_INTERVAL:
            main_rev(
                rev_range_since.strftime("%Y-%m-%d %H:%M"),
                rev_range_end.strftime("%Y-%m-%d %H:%M"),
            )
            remove_unchanged(config["mongo_config"]["connection_string"])
            rev_range_since += REV_INTERVAL

        # Run spider
        run(main)
