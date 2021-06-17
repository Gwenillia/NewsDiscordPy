from defs import *


@bot.event
async def on_ready():
    # create tables
    c.execute('''
        CREATE TABLE IF NOT EXISTS guild
        (
            ID INTEGER PRIMARY KEY NOT NULL,
            guild_id INTEGER NOT NULL,
            prefix VARCHAR(3) NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS flux
        (
            ID INTEGER PRIMARY KEY NOT NULL,
            guild_id INTEGER NOT NULL REFERENCES guild(ID),
            url VARCHAR(2083) NOT NULL,
            flux_name VARCHAR(40) NOT NULL,
            channel INT NOT NULL,
            UNIQUE (url, flux_name, channel)
        )
    ''')

    for cog in COGS:
        try:
            bot.load_extension(cog)
        except Exception:
            print(f'Unable to load {cog}')
        else:
            print(f'{cog}Extensions loaded')

    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name="les actualités"))
    feed_multi_news_rss.start(bot)
    print(f'{bot.user.name} is running on {len(bot.guilds)} guild')

@bot.event
async def on_guild_join(guild):
    prefix = ";"
    # check if guild is already saved in db and add it or not
    c.execute('''
        INSERT INTO guild (guild_id, prefix)
        SELECT ?, ?
        WHERE NOT EXISTS (
            SELECT 1 FROM guild WHERE guild_id=? AND prefix=?
            )''', (guild.id, prefix, guild.id, prefix))

    db.commit()


if __name__ == '__main__':
    bot.run(TOKEN, bot=True, reconnect=True)
