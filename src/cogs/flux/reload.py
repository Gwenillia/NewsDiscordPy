from defs import *


class Reload(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="reload", aliases=['r'], usage="reload", help="Recharge les flux en mémoire")
    async def reload(self, ctx):
        try:
            load_param_csv()
        except ValueError:
            emb = discord.Embed(description='Un **problême** est survenu lors du rechargement du fichier csv. :sob:',
                                color=DEFAULT_COLOR)
            await send_embed(ctx, emb)

        emb = discord.Embed(description='Le fichier csv a été **rechargé**. :100:', color=DEFAULT_COLOR)
        await send_embed(ctx, emb)


def setup(bot):
    bot.add_cog(Reload(bot))
