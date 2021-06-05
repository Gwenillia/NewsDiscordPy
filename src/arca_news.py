from defs import *

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        try:
            bot.load_extension(f'cogs.{filename[:-3]}')
            print(f'cogs.{filename[:-3]}')
        except ImportError:
            print(f'Unable to load {filename[:-3]}')


@bot.event
async def on_ready():
    load_param_csv()
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name="les actualités"))
    feed_multi_news_rss.start(bot)
    print(f'{bot.user.name} is running on {len(bot.guilds)} guild')


bot.run(TOKEN, bot=True, reconnect=True)
