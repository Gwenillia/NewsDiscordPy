from datetime import datetime

from discord.ext import tasks

from defs import *

def run():
    @bot.event
    async def on_ready():
        load_param_csv()
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="les actualités"))
        feed_multi_news_rss.start()
        print('bot is running')

    @tasks.loop(seconds=10)
    async def feed_multi_news_rss():
        global date
        global titles
        if datetime.fromtimestamp(time.time()).day != datetime.fromtimestamp(date).day:
            date = time.time()
            titles = []
            load_param_csv()

        functions = []

        for row in PARAM_CSV:
            function = asyncio.create_task(feed_news_rss(row))
            functions.append(function)

        await asyncio.gather(*functions)

    bot.run(token)


if __name__ == '__main__':
    run()
