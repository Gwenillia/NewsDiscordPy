from defs import *


@bot.event
async def on_ready():
    for cog in COGS:
        try:
            bot.load_extension(cog)
        except Exception:
            print(f'Unable to load {cog}')
        else:
            print(f'{cog}Extensions loaded')

    load_param_csv()
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name="les actualités"))
    feed_multi_news_rss.start(bot)
    print(f'{bot.user.name} is running on {len(bot.guilds)} guild')


if __name__ == '__main__':
    bot.run(TOKEN, bot=True, reconnect=True)
