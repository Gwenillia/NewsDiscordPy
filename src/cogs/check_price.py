import os
import uuid

import discord
from defs import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class CheckPrice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="checkPrice", usage="checkPrice <nom d'un jeux>",
                      help="Donne une liste pour trouver un jeux au prix les plus bas")
    async def check_price(self, ctx, *args):
        if args is None:
            await ctx.author.send('Tu dois préciser le nom d\'un jeux')
            return

        async with ctx.typing():
            uid = uuid.uuid1()
            FIREFOX_HEADER_OPTIONS.headless = True
            driver = webdriver.Firefox(options=FIREFOX_HEADER_OPTIONS)
            wait = WebDriverWait(driver, 30)
            scrapped_link = f"https://www.goclecd.fr/catalogue/category-pc-games-all/search-{'+'.join(args)}/sort-relevance-asc/"
            driver.get(scrapped_link)
            wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                                                'div.aks-lazyloaded'))).get_attribute(
                "style")
            list = driver.find_element_by_class_name('search-results')
            try:
                with open(f"temp_list_image-{uid}.png", "wb") as temp_list_img:
                    temp_list_img.write(list.screenshot_as_png)
            except Exception:
                print('Can\'t save image')

        e = discord.Embed(title="Voici ce que j'ai trouvé !", url=scrapped_link, color=DEFAULT_COLOR)
        file = discord.File(temp_list_img.name, filename=temp_list_img.name)
        e.set_image(url="attachment://" + temp_list_img.name)
        await ctx.send(file=file, embed=e)
        os.remove(temp_list_img.name)

        driver.close()


def setup(bot):
    bot.add_cog(CheckPrice(bot))
