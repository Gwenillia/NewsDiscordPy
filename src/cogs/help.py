from discord.ext import commands
import discord

from src.defs.get_prefix import get_prefix
from src.consts import DEFAULT_COLOR
from src.defs import send_embed


class Help(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

  @commands.command(name="help", aliases=['h'], usage="help", help="Affiche la commande help")
  async def help(self, ctx, *input):
    if not input:
      emb = discord.Embed(title='Commandes', color=DEFAULT_COLOR,
                          description=f'Utilises `{await get_prefix(self.bot, ctx)}help <commande>` pour avoir plus d\'informations sur une commande :relieved:\n')

      cogs_desc = ''
      for cog in self.bot.cogs:

        for command in self.bot.get_cog(cog).get_commands():
          cogs_desc += f'`{command.name.partition(" ")[0]}`'
          if command.aliases:
            cogs_desc += f'/`{"/ ".join(command.aliases)}`\n'
          else:
            cogs_desc += f'\n'

      emb.add_field(name='Commandes', value=cogs_desc, inline=False)

      commands_desc = ''
      for command in self.bot.walk_commands():
        if not command.cog_name and not command.hidden:
          commands_desc += f'{command.name} - {command.help}\n'

      if commands_desc:
        emb.add_field(name='N\'appartient à aucune commande', value=commands_desc, inline=False)

    elif len(input) == 1:
      for cog in self.bot.cogs:
        if cog.lower() == input[0].lower():
          emb = discord.Embed(title=f'Commande - {cog}', color=DEFAULT_COLOR)

          for command in self.bot.get_cog(cog).get_commands():
            if not command.hidden:
              emb.add_field(name=f'`{await get_prefix(self.bot, ctx)}{command.usage}`', value=command.help, inline=False)
          break

        else:
          emb = discord.Embed(title="Commande inexistante",
                              description=f'Il n\'existe pas de commande `{input[0]}` :sweat:',
                              color=DEFAULT_COLOR)

    elif len(input) > 1:
      emb = discord.Embed(title='Stop', description='Une seule commande à la fois :sweat_smile:',
                          color=DEFAULT_COLOR)

    else:
      emb = discord.Embed(title='Meh', description='Tu es un magicien. Tu n\'est pas censé arriver là...',
                          color=DEFAULT_COLOR)

    await send_embed(ctx, emb)


def setup(bot):
  bot.add_cog(Help(bot))
