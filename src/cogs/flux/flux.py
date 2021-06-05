from defs import *


class Flux(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="flux", help="Affiche la liste des flux et leur channels", usage="flux")
    async def flux(self, ctx):
        emb = discord.Embed(title="Voici la liste des flux actuellement en vigueur", color=DEFAULT_COLOR)
        for param in PARAM_CSV:
            emb.add_field(name=param["name"], value=f'<#{param["channel"]}>', inline=False)

        await send_embed(ctx, emb)


def setup(bot):
    bot.add_cog(Flux(bot))
