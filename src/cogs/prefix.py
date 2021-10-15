import discord
from discord.ext import commands

from defs import send_embed
from src.consts import c, db


class Prefix(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

  @commands.command(name='prefix', aliases=['pre'], help="Change le prefix du bot sur le serveur",
                    usage="prefix <nouveau prefix>")
  @commands.has_permissions(manage_channels=True)
  @commands.bot_has_permissions(manage_channel=True)
  async def prefix(self, ctx, new_prefix: str = None):
    if new_prefix is None:
      await ctx.send("Tu dois préciser un prefix pour que je puisse le changer :relieved:")
      return

    c.execute('''
            UPDATE guild SET prefix = ? WHERE guild_id = ?
        ''', (new_prefix, ctx.message.guild.id))
    db.commit()
    await ctx.send(f'Le prefix a bien été changé pour {new_prefix}')

  @prefix.error
  async def handle_error(self, ctx, error):
    if isinstance(error, commands.MissingPermissions):
      emb = discord.Embed(description="Tu n'as pas la permission pour faire cela :sob:", color=0xff0000)
      await send_embed(ctx, emb)

    elif isinstance(error, commands.BotMissingPermissions):
      emb = discord.Embed(description="Désolé, je n'ai pas les permissions de faire ça :sob:", color=0xff0000)
      await send_embed(ctx,emb)

def setup(bot):
  bot.add_cog(Prefix(bot))
