#!/usr/bin/python3

from discord.ext import commands
import discord
from src.defs.rss import feed_multi_news_rss
from src.consts import bot, c, COGS, db, TOKEN, get_prefix


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
    except (ModuleNotFoundError, commands.ExtensionNotFound)  as ex:
      template = "Unable to load {0}.\n{1}:{2!r}"
      message = template.format(cog, type(ex).__name__, ex.args)
      print(message)
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


@bot.event
async def on_message(message):
  try:
    prefix = await get_prefix(bot, message)
  except TypeError:
    # check if guild is already saved in db and add it or not
    prefix = ";"
  c.execute('''
            INSERT INTO guild (guild_id, prefix)
            SELECT ?, ?
            WHERE NOT EXISTS (
                SELECT 1 FROM guild WHERE guild_id=? AND prefix=?
                )''', (message.guild.id, prefix, message.guild.id, prefix))

  db.commit()
  await bot.process_commands(message)


if __name__ == '__main__':
  bot.run(TOKEN, bot=True, reconnect=True)
