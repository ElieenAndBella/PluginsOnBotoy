import httpx
import time
import re

from botoy import Action, GroupMsg
from botoy.decorators import ignore_botself, these_msgtypes


def get_online_num(bvid: str, cid: str) -> str:
    resp = httpx.get(f"http://api.bilibili.com/x/player/online/total?bvid={bvid}&cid={cid}")
    online_nums = resp.json()['data']['total']
    return online_nums


def get_bvid(url: str) -> str:
    resp = httpx.get(url, allow_redirects=False)
    print(resp.headers)
    bvid = re.match(".*/video/(.*)\?.*", resp.text)
    return bvid.group(1)


def get_bili_video_detail(bvid: str):
    resp = httpx.get("https://api.bilibili.com/x/web-interface/view?bvid=" + bvid)
    cid = resp.json()['data']['cid']
    online = get_online_num(bvid, cid)
    stat = resp.json()['data']['stat']
    cover = resp.json()['data']['pic']
    title = resp.json()['data']['title']
    pubdate = resp.json()['data']['pubdate']
    desc = resp.json()['data']['desc']
    favorite = stat['favorite']
    view = stat['view']
    danmaku = stat['danmaku']
    reply = stat['reply']
    coin = stat['coin']
    share = stat['share']
    like = stat['like']

    text = f"""名称：{title}
发布日期：{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(pubdate)))}
描述：{desc}
观看数：{view}
点赞数：{like}
投币数：{coin}
收藏数：{favorite}
弹幕数：{danmaku}
评论数：{reply}
分享数：{share}
在线观看人数：{online}"""

    return cover, text


def bili_video_parse(ctx):
    short = re.match(".*url=.*?\"(.*)\?.*", eval(ctx.Content)["Content"]).group(1)
    if short:
        cover, text = get_bili_video_detail(get_bvid(short))

        Action().sendGroupPic(ctx.FromGroupId, picUrl=cover, content=text)
    else:
        return


@ignore_botself
@these_msgtypes("XmlMsg")
def receive_group_msg(ctx: GroupMsg):
    bili_video_parse(ctx)
