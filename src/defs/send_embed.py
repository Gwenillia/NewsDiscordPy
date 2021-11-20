from discord.errors import Forbidden

async def send_embed(ctx, embed):
    try:
        await ctx.send(embed=embed)
    except Forbidden:
        await ctx.author.send(
            f"Je ne peut pas envoyer de message dans {ctx.channel.name} on {ctx.guild.name} :cold_sweat:",
            embed=embed
        )