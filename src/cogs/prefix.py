from defs import *


class Prefix(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='prefix', help="Change le prefix du bot sur le serveur", usage="prefix <nouveau prefix>")
    async def prefix(self, ctx, new_prefix: str = None):
        if new_prefix is None:
            await ctx.send("Tu dois préciser un prefix pour que je puisse le changer :relieved:")
            return

        c.execute('''
            UPDATE guild SET prefix = ? WHERE guild_id = ?
        ''', (new_prefix, ctx.message.guild.id))
        db.commit()
        await ctx.send(f'Le prefix a bien été changé pour {new_prefix}')


def setup(bot):
    bot.add_cog(Prefix(bot))
