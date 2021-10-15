from discord.ext import commands
import discord
from src.defs import send_embed
from src.consts import DEFAULT_COLOR

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping", help="Test la latence entre client et le serveur", usage='ping')
    async def ping(self, ctx):
        emb = discord.Embed(title=f'pong - {round(self.bot.latency * 1000)}ms', color=DEFAULT_COLOR)
        await send_embed(ctx, emb)


def setup(bot):
    bot.add_cog(Ping(bot))
