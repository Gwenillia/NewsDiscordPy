import json
import logging

import discord
from discord.ext import commands

from src.config import Config
from src.database import Database
from src.defs.get_prefix import get_prefix
from src.defs.rss import feed_multi_news_rss


class Bot(commands.Bot):
  def __init__(self):
    super().__init__(
      command_prefix=get_prefix,
      help_command=None,
      case_insensitive=True
    )

    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)

    with open('src/config.json', 'r') as f:
      self.cfg = Config(json.loads(f.read()))

    self.db = Database(self.loop, self.cfg.postgresql_user, self.cfg.postgresql_password)

    self.cog_list = [
      'src.cogs.help',
      'src.cogs.ping',
      'src.cogs.flux.add_rss',
      'src.cogs.flux.del_rss',
      'src.cogs.flux.flux',
      'src.cogs.check_price',
      'src.cogs.prefix',
      'src.cogs.ranking'
    ]

    for cog in self.cog_list:
      try:
        self.load_extension(cog)
        print("Cog {0} has been loaded !".format(cog))
      except (ModuleNotFoundError, commands.ExtensionNotFound) as ex:
        print("Unable to load {0}.\n{1}:{2!r}".format(cog, type(ex).__name__, ex.args))

  async def on_ready(self):
    feed_multi_news_rss.start(self)
    print("{0} is running on {1} guilds".format(self.user.name, len(self.guilds)))
    await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="les actualités"))

  async def on_guild_join(self, guild):
    await self.db.execute('INSERT INTO guild (discord_guild_id, prefix) SELECT $1, $2 ON CONFLICT DO NOTHING', guild.id,
                          ';')

  async def on_message(self, message):
    await self.process_commands(message)

  def startup(self):
    self.run(self.cfg.bot_token, bot=True, reconnect=True)


if __name__ == '__main__':
  Bot().startup()
