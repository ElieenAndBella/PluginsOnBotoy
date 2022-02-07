"""
A-SOUL日程表
"""
import os
import jsonpath
import datetime

from aiohttp import ClientSession

from botoy import S, GroupMsg, Action
from botoy.contrib import get_cache_dir
from botoy.async_decorators import ignore_botself, equal_content

cache_path = get_cache_dir("bot_schedule_table")
if os.path.exists(cache_path / "schedule.txt") is False:
    open(cache_path / "schedule.txt", "w").close()

null = ""


async def recode_txt(img_list):
    if read_last_txt() != f"{datetime.date.today()} {img_list}\n":
        with open(cache_path / "schedule.txt", "a")as f:
            f.write(f"{datetime.date.today()} {img_list}\n")


def read_last_txt():
    with open(cache_path / "schedule.txt", "r")as f:
        try:
            record = f.readlines()[-1]
        except:
            return ""
    return record


async def get_picORpics(respJson) -> list:
    '''
    获取日程表图片链接
    :return: 日程表图片列表
    '''
    _cards = jsonpath.jsonpath(respJson, "$..cards")[0]
    for _card in _cards:
        _card = jsonpath.jsonpath(_card, "$..card")[0]
        if "日程表" in _card:
            _origin = jsonpath.jsonpath(eval(_card), "$..origin")
            if _origin:
                _ = jsonpath.jsonpath(eval(_origin[0]), "$..item.pictures")[0]
                break
            else:
                _ = jsonpath.jsonpath(eval(_card), "$..pictures")[0]
                break
    try:
        response = [__["img_src"].replace("\\", "") for __ in _]
        return response
    except:
        return []


async def getScheduler() -> str:
    async with ClientSession() as session:
        async with session.get(
                "https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?visitor_uid=0&host_uid=703007996&offset_dynamic_id=0&need_top=1&platform=web",
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.62"
                }) as response:
            receive = await response.json()
            img_list = await get_picORpics(receive)
            if img_list == []:
                resp = read_last_txt()
                img_list = eval(resp.split()[-1])
                if img_list == []:
                    '''
                        照常理来说是不会走这里的，因为我有采取缓存，会执行到这里只有两种原因
                        如果走这里，说明Asoul动态第一页已经没有关于日程表的相关信息，就需要用户自己将第二页的日程表按格式加入schedule.txt，
                        如果自己有能力可以写一个循环动态，直到获取到日程表，如何获取日程表我已经写好了，你只需要暴力搜索即可
                        
                        获取动态页面的链接，返回格式为JSON
                        https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?visitor_uid=0&host_uid=703007996&offset_dynamic_id=0&need_top=1&platform=web
                        更改offset_dynamic_id即可获取下一页，offset_dynamic_id是动态更改的，每次response会返回相关字段
                        
                        要出现这种情况太极端了，所以我懒得写了，追求完美的人可以完善一下，提个PR
                    '''
                    return "没有日程表欸，可以稍后或者隔天试试"
            await recode_txt(img_list)
            return img_list


@ignore_botself
@equal_content("日程表")
async def receive_group_msg(ctx: GroupMsg):
    resp = await getScheduler()
    if isinstance(resp, str):
        S.bind(ctx).text(resp)
    elif isinstance(resp, list):
        resp = [Action().getGroupPicInfo(url=r)["PicInfo"]["PicMd5"] for r in resp]
        S.bind(ctx).image(resp)
