import json
from urllib.parse import urljoin, urlparse

import discord
import requests
from discord.ext import commands

from src.consts import DEFAULT_COLOR
from src.defs import send_embed


def get_input_game_id(input_game):
  req = requests.get('https://www.allkeyshop.com/api/v2/vaks.php?action=gameNames&currency=eur')
  res = json.loads(req.text)
  for item in res['games']:
    if input_game in item['name'].lower():
      input_game_id = item['id']
      return input_game_id, item['name']


def get_game_data(input_game_id):
  req = requests.get(f'https://www.allkeyshop.com/blog/wp-admin/admin-ajax.php?action=get_offers&product='
                     f'{input_game_id}&currency=eur&region=&moreq=&use_beta_offers_display=1')
  res = json.loads(req.text)
  offers = []
  for item in res['offers'][:5]:
    # merchant
    merchant_id = item['merchant']
    merchant_name = res['merchants'][merchant_id]['name']

    if "microsoft" in merchant_name.lower():
      pass
    else:
      # price
      price = item['price']['eur']['priceWithoutCoupon']
      # edition
      edition_id = item['edition']
      edition_name = res['editions'][edition_id]['name']
      # region
      region_id = item['region']
      region_name = res['regions'][region_id]['name']
      # platform
      platform = item['platform']
      # url
      affiliate_url = item['affiliateUrl']
      url = urljoin(affiliate_url, urlparse(affiliate_url).path)

      offer = Offer(price, edition_name, merchant_name, region_name, platform, url)
      offers.append(offer)
  return offers


class Offer:
  def __init__(self, price, edition_name, merchant_name, region_name, platform, url):
    self.price = price
    self.edition = edition_name
    self.merchant = merchant_name
    self.region = region_name
    self.platform = platform
    self.url = url


class CheckPrice(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(name="checkPrice", aliases=['cp'], usage="checkPrice <nom d'un jeux>",
                    help="Donne une liste pour trouver un jeux au prix les plus bas")
  async def check_price(self, ctx, *args):
    if len(args) < 1:
      await ctx.send('Tu dois préciser le nom d\'un jeux')
      return

    async with ctx.typing():
      input_game = ' '.join(args).lower()
      game = get_input_game_id(input_game)
      game_id = game[0]
      game_name = game[1]
      game_data = get_game_data(game_id)
      emb = discord.Embed(
        title=f'{game_name} :100:',
        color=DEFAULT_COLOR
      )
      for item in game_data:
        emb.add_field(name="————————————————————",
                      value=f'Boutique: [**{item.merchant}**]({item.url}) \nPrix: **{item.price}€** \nÉdition: **{item.edition}** \nActivable uniquement sur **{item.platform}** en **{item.region}**',
                      inline=False)
    await send_embed(ctx, emb)


def setup(bot):
  bot.add_cog(CheckPrice(bot))
