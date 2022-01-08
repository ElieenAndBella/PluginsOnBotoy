"""
使用：日程表

A_soul 日程表
"""
import os
import re
import datetime
from aiohttp import ClientSession

from botoy import S, GroupMsg
from botoy.contrib import get_cache_dir
from botoy.async_decorators import ignore_botself, equal_content

bst = get_cache_dir("bot_schedule_table")
schedule_path = bst / "schedule.txt"
open(schedule_path, "w").close()


async def getScheduler() -> str:
    async with ClientSession() as session:
        async with session.get(
                "https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?visitor_uid=0&host_uid=703007996&offset_dynamic_id=0&need_top=1&platform=web",
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.62"
                }) as response:
            _ = "save url e.g"
            receive = await response.text()
            today = str(datetime.date.today())
            re_res = re.findall("日程表.*?img_src.*?(https.*?jpg)", receive)
            with open(schedule_path, "r", encoding="utf-8")as f:
                content = f.readlines()
                try:
                    _ = content[-1].strip()
                except:
                    pass
            with open(schedule_path, "a", encoding="utf-8")as f:
                # _ = https://i0.hdslb.com/bfs/album/6bd363cb04051f8292910f6a7c26fd71375b3204.jpg 2022-01-06
                if not re_res:
                    print(__file__, "没有日程表，采取缓存")
                    return _.split()[0]
                elif _ != (re_res[0].replace('\\', '') + " " + today):
                    f.write(re_res[0].replace('\\', '') + " " + today + "\n")
                    return re_res[0].replace('\\', '')
                else:
                    print(__file__, "日程表没有更新")
                    return _.split()[0]


@ignore_botself
@equal_content("日程表")
async def receive_group_msg(ctx: GroupMsg):
    bstUrl = await getScheduler()
    S.bind(ctx).image(bstUrl)
