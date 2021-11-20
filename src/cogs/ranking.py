import json
from asyncio import sleep
from random import randint

import discord
from discord.ext import commands

from src.config import Config
from src.database import Database
from src.defs import send_embed


def needed_xp(level):
  return 100 + level * 80


class Ranking(commands.Cog):
  def __init__(self, bot):
    with open('src/config.json', 'r') as f:
      self.cfg = Config(json.loads(f.read()))

    self.bot = bot
    self.brake = []
    self.db = Database(self.bot.loop, self.cfg.postgresql_user, self.cfg.postgresql_password)

  @commands.Cog.listener()
  async def on_message(self, message):
    if (message.author.id != self.bot.user.id) and (message.author.id not in self.brake):
      try:
        # Find if a member exists
        req = await self.db.fetch(
          'SELECT EXISTS(SELECT 1 FROM member m JOIN "user" u ON m.USER_ID = u.ID JOIN guild g on m.GUILD_ID = g.ID WHERE u.discord_user_id = $1 AND g.discord_guild_id = $2)',
          message.author.id, message.guild.id
        )
        res = req[0][0]

        if res is False:
          # member doesn't exists so we try to select the user
          req = await self.db.fetch('SELECT EXISTS(SELECT 1 FROM "user" WHERE discord_user_id = $1)', message.author.id)
          res = req[0][0]

          if res is False:
            # user doesn't exist so we create it and create a member out of it
            await self.db.execute(
              'INSERT INTO "user" (discord_user_id) VALUES ($1)', message.author.id)
            await self.db.execute(
              'INSERT INTO member (GUILD_ID, USER_ID, level, xp) SELECT guild.ID, "user".ID, $1, $2 FROM guild, "user" WHERE discord_guild_id = $3 AND discord_user_id = $4',
              0, 0, message.guild.id, message.author.id
            )

          else:
            # user exists but no member found
            await self.db.execute(
              'INSERT INTO member (GUILD_ID, USER_ID, level, xp) SELECT guild.ID, "user".ID, $1, $2 FROM guild, "user" WHERE discord_guild_id = $3 AND discord_user_id = $4',
              0, 0, message.guild.id, message.author.id
            )

        else:
          # user and member found so we can get the level and xp from the member and proceed
          req = await self.db.fetch('''
            SELECT level, xp 
            FROM member m 
            JOIN "user" u ON m.user_id = u.ID 
            JOIN guild g ON m.guild_id = g.ID
            WHERE u.discord_user_id = $1 AND g.discord_guild_id = $2
          ''', message.author.id, message.guild.id)

          res = req[0]

          current_xp = res[1] + randint(self.bot.cfg.min_message_xp, self.bot.cfg.max_message_xp)

          if current_xp >= needed_xp(res[0]):
            # level up and set xp to 0
            # TODO : stop setting xp to 0 and set xp wih the extra points
            await self.db.execute('''
              UPDATE member SET level = $1, xp = $2
              WHERE $3 IN (SELECT discord_user_id FROM "user") AND $4 IN (SELECT discord_guild_id FROM guild)
            ''', res[0] + 1, 0, message.author.id, message.guild.id)

          else:
            # just update xp cuz not enough xp to level up
            await self.db.execute('''
              UPDATE member SET xp = $1
              WHERE $2 in (SELECT discord_user_id FROM "user") AND $3 IN (SELECT discord_guild_id FROM guild)
            ''', current_xp, message.author.id, message.guild.id)

          self.brake.append(message.author.id)
          await sleep(randint(15, 25))
          self.brake.remove(message.author.id)

      except Exception as ex:
        print('error {0}:{1!r}'.format(type(ex).__name__, ex.args))

  @commands.command(name="rank", usage="rank", help="Permet de voir son level et son xp sur le serveur")
  async def rank(self, ctx):
    req = await self.db.fetch('''
      SELECT level, xp FROM member m
      JOIN "user" u ON m.user_id = u.id
      JOIN guild g ON m.guild_id = g.id
      WHERE u.discord_user_id = $1 AND g.discord_guild_id = $2
    ''', ctx.author.id, ctx.guild.id)

    res = req[0]

    if res:
      emb = discord.Embed(
        description='Tu es lv **{0}**, et tu as **{1}**xp. Plus que **{2}**xp pour level up :relieved:'.format(
          res[0], res[1], needed_xp(res[0])))
      await send_embed(ctx, emb)


def setup(bot):
  bot.add_cog(Ranking(bot))
