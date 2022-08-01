# weibo-anti-censorship
This is currently only a placeholder.

## Idea
To track and archive all the censored/removed posts posted or reposted by your following users.

Save all posts in your feed for ~2 days, archive all posts that are removed or edited.

每20分钟抓取新微博

每24小时进行一次回溯检测，检查任何内容存在变动的微博（转发的原博被夹）

暂时不确定怎么检测被夹的转发和原创

考虑放在一个新collection里面

**Modified case:**

coll = weibo
```json
{
    "id":"a",
    "content":"AA",
}
```
coll = weibo_rev
```json
{
    "id":"a",
    "content":"BB",
}
```

**Deleted case:**

coll = weibo
```json
{
    "id":"a",
    "content":"AA",
}
```

coll = weibo_rev
```json
{}
```
如果距离发布日期已过去24小时，则从数据库中移除:

**OK case** (to be removed from `weibo` coll) (at 2022-07-23 13:01):

coll = weibo
```json
{
    "id":"a",
    "content":"AA",
    "publish_time":"2022-07-22 13:00",
}
```

coll = weibo_rev
```json
{
    "id":"a",
    "content":"AA",
    "publish_time":"2022-07-22 13:00",
}
```

现在需要实现的功能有：
- 允许将 config_file 作为 weibo_spider 的 argument
- 指定 collection in MongoDB
- 删除两个 collections 的交集


## Example

2022-07-20 13:00 开始运行

2022-07-20 13:20 爬取过去20分钟（2022-07-20 13:00 - 13:20）的关注列表微博,存入`weibo` collection。

2022-07-20 13:40 爬取过去20分钟（2022-07-20 13:20 - 13:40）的关注列表微博。

...

2022-07-22 13:00 回溯检测，爬取48小时前至24小时前（2022-07-20 13:00 - 2022-07-21 13:00）的关注列表微博,存入`weibo_rev` collection。

2022-07-22 13:00 删除`weibo`和`weibo_rev`两个collections的交集。

此时`weibo_rev` collection中没有doc。

`weibo` collection中存有2022-07-20 13:00至2022-07-21 13:00被夹的微博，
以及2022-07-21 13:00至2022-07-22 13:00的所有微博

...


## 另一种回溯检测的思路

与爬取定时相同，每20分钟检测。

根据`weibo` collection中，`publish_time`已过去24小时的docs中id进行精准爬取。

即是每次回溯检测只需要爬取20分钟区间的内容。

根据`publish_time`顺序排序，逐个检查，如果内容没有发生变化则删除，如果`publish_time`时间差小于24小时则停止检测。

又或者：将主程序分为两个并行的脚本，脚本0使用`user_id_list.txt`设置文件（可以自动更新since date），脚本1使用整数范围日期（但是不知道怎么设置end date）。


## Run script

```bash
$ python3 -m wbac
```