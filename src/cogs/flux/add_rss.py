import ssl

from defs import *


class AddRss(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="addRss", usage="addRss <nom du flux> <lien vers le flux> <#channel>",
                      help='Permet d\'ajouter un flux RSS')
    async def add_rss(self, ctx, rules_name: str = None, flux_rss: str = None, channel: str = None):

        global date
        date = time.time()
        try:
            # Monkeypatching certificat
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            pass
        else:
            ssl._create_default_https_context = _create_unverified_https_context
        if rules_name is None or flux_rss is None or channel is None:
            await send_embed(ctx, discord.Embed(description='Il manque des arguments. Commande **help** :sweat_smile:',
                                                color=DEFAULT_COLOR))
            return
        try:
            channel_id = int(channel[2:len(channel) - 1])
        except ValueError:
            await send_embed(ctx,
                             discord.Embed(
                                 description=f'Un problème est survenue avec le channel **{channel}**. :sob:',
                                 color=DEFAULT_COLOR))
            return
        if not re.fullmatch(".*[a-zA-Z0-9]", rules_name):
            emb = discord.Embed(
                description=f'Tu as mis des caractères spéciaux dans le nom : **{rules_name}**. :sweat_smile:',
                color=DEFAULT_COLOR)
        elif bot.get_channel(channel_id) is None:
            emb = discord.Embed(description='Tu as mis un **channel non valide**. :sweat_smile:', color=DEFAULT_COLOR)
        elif len(feedparser.parse(flux_rss).entries) == 0:
            emb = discord.Embed(description=f'Ton flux rss **{flux_rss}** ne retourne rien. :sweat_smile:',
                                color=DEFAULT_COLOR)
        else:
            row_contents = {
                "fluxrss": flux_rss,
                "name": rules_name,
                "channel": channel_id
            }
            try:
                PARAM_CSV.append(row_contents)
                write_param_csv()
                emb = discord.Embed(description=f'Le flux de news : **{rules_name}** a correctement été ajouté ! :100:',
                                    color=DEFAULT_COLOR)
            except ValueError:
                PARAM_CSV.remove(row_contents)
                emb = discord.Embed(
                    description='Une erreur s\'est produite lors de la sauvegarde du flux rss. Désolé :sob:',
                    color=DEFAULT_COLOR)

        await send_embed(ctx, emb)


def setup(bot):
    bot.add_cog(AddRss(bot))
