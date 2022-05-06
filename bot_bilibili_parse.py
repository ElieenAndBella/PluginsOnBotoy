"""BiliBili视频解析，关爱电脑党"""
import httpx
import time
import re
from PIL import Image
from io import BytesIO

from botoy import Action, GroupMsg
from botoy.decorators import ignore_botself
from pyzbar.pyzbar import decode

bot = Action()


def from_img_get_url(picUrl=None):
    barcodes = decode(Image.open(BytesIO(httpx.get(picUrl).content)))
    parse_url = ""
    for barcode in barcodes:
        parse_url = barcode.data.decode("utf-8")
    print("bilibili_parse::from_img_get_url=>", parse_url)
    return parse_url


def get_online_num(bvid: str, cid: str) -> str:
    resp = httpx.get(f"http://api.bilibili.com/x/player/online/total?bvid={bvid}&cid={cid}")
    online_nums = resp.json()['data']['total']
    return online_nums


def get_bvid(url: str) -> str:
    resp = httpx.get(url, allow_redirects=False)
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
描述：{desc.strip()}
观看数：{view}
点赞数：{like}
投币数：{coin}
收藏数：{favorite}
弹幕数：{danmaku}
评论数：{reply}
分享数：{share}
在线观看人数：{online}
链接：https://www.bilibili.com/video/{bvid}"""

    return cover, text


def bili_video_parse_by_xml(ctx, url=None):
    if ctx.MsgType != "XmlMsg":
        return
    _ = eval(ctx.Content)["Content"] if url == None else url
    try:
        short = re.match(".*url=.*?\"(.*)\?.*", _).group(1)
    except AttributeError:
        return
    cover, text = get_bili_video_detail(get_bvid(short))
    bot.sendGroupPic(ctx.FromGroupId, picUrl=cover, content=text)
    return


def bili_video_parse_by_url(ctx, url=None):
    if ctx.MsgType == "XmlMsg":
        return
    _ = ctx.Content if url == None else url
    if (temp := re.match(".*(http[s]?://[w]{0,3}\.?b23.tv/\w+)\s*", _)) != None:
        cover, text = get_bili_video_detail(get_bvid(temp.group(1)))
        bot.sendGroupPic(ctx.FromGroupId, picUrl=cover, content=text)
        return
    if (temp := re.match(".*http[s]?://[w]{0,3}\.?bilibili.com/video/(\w+)\s*", _)) != None:
        cover, text = get_bili_video_detail(temp.group(1))
        bot.sendGroupPic(ctx.FromGroupId, picUrl=cover, content=text)
        return


def bili_video_parse_by_bv(ctx, url=None):
    if ctx.MsgType == "XmlMsg":
        return
    _ = ctx.Content if url == None else url
    if (temp := re.match(".*(^(BV)[a-zA-Z0-9]+$\s*)", _)) != None:
        cover, text = get_bili_video_detail(temp.group(1))
        bot.sendGroupPic(ctx.FromGroupId, picUrl=cover, content=text)
        return


def bili_video_parse_by_img(ctx):
    if ctx.MsgType == "XmlMsg":
        return
    # 判断消息中是否含有图片
    try:
        if "GroupPic" not in eval(ctx.Content):
            return
    except (TypeError, NameError, SyntaxError, AttributeError):
        return
    for url in [from_img_get_url(gp["Url"]) for gp in eval(ctx.Content)["GroupPic"]]:
        bili_video_parse_by_xml(ctx, url)
        bili_video_parse_by_url(ctx, url)
        bili_video_parse_by_bv(ctx, url)


@ignore_botself
def receive_group_msg(ctx: GroupMsg):
    bili_video_parse_by_xml(ctx)
    bili_video_parse_by_url(ctx)
    bili_video_parse_by_bv(ctx)
    bili_video_parse_by_img(ctx)
