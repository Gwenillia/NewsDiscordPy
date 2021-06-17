from defs import *


class Flux(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="flux", help="Affiche la liste des flux et leur channels", usage="flux")
    async def flux(self, ctx):
        req = c.execute('''
            SELECT flux_name, channel FROM flux WHERE guild_id = ?
        ''', (ctx.message.guild.id,))
        fluxs = req.fetchall()

        emb = discord.Embed(title="Voici la liste des flux actuellement en vigueur", color=DEFAULT_COLOR)

        for flux in fluxs:
            emb.add_field(name=flux[0], value=flux[1], inline=False)

        await send_embed(ctx, emb)


def setup(bot):
    bot.add_cog(Flux(bot))
