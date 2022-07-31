from weibo_spider.spider import main
from absl import app
import time

SLEEP_TIME = 1200

"""
每20分钟抓取新微博
每12小时进行一次回溯检测，检查任何内容存在变动的微博（转发的原博被夹）
暂时不确定怎么检测被夹的转发和原创
考虑放在一个新collection里面
Modified case:
    weibo
    {
        id:"a",
        content:"AA",
    }

    weibo_revisited
    {
        id:"a",
        content:"BB",
    }

Deleted case:
    weibo
    {
        id:"a",
        content:"BB",
    }

    weibo_revisited
    {}

如果距离发布日期已过去24小时，则从数据库中移除:
OK case (to be removed from weibo coll) (at 2022-07-23 13:01):
    weibo
    {
        id:"a",
        content:"AA",
        publish_time:"2022-07-22 13:00",
    }

    weibo_revisited
    {
        id:"a",
        content:"AA",
        publish_time:"2022-07-22 13:00",
    }
"""

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
