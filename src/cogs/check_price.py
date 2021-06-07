import os
import uuid

import discord
import selenium.common.exceptions
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
            wait = WebDriverWait(driver, 10)
            scrapped_link = "https://www.goclecd.fr/"
            driver.get(scrapped_link)
            # next line need fix
            try:
                wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'banner-search-form-input')))
            except selenium.common.exceptions.TimeoutException as ex:
                await ctx.send(
                    "Tiens, le site que j'utilise a totalement changé, désolée mais je dois subir une màj :sweat_smile:")
            search_input = driver.find_element_by_class_name("banner-search-form-input")
            search_input.clear()
            search_input.send_keys("+".join(args))

            # next line need fix
            try:
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'ls-results-row-image')))
            except selenium.common.exceptions.TimeoutException as ex:
                await ctx.send("y'a R frèr")
                return

            first_result = driver.find_element_by_css_selector(".ls-results-row-image:first-of-type")

            first_result.click()

            wait.until(EC.presence_of_element_located((By.ID, 'offer_offer')))

            url = driver.current_url

            driver.execute_script("""
                let a = document.getElementById('offers_table');
                for(i = a.children.length; i > 6; i--) {
                    a.lastChild.remove();
                };
                let style = `
                    <style>
                        .metacritic-button { display: none; }
                        .buy-btn-cell { display: none; }
                    </style>
                `
                document.head.insertAdjacentHTML("beforeend", style);
            """)

            list = driver.find_element_by_id('offers_table')

            try:
                with open(f"temp_list_image-{uid}.png", "wb") as temp_list_img:
                    temp_list_img.write(list.screenshot_as_png)
            except Exception:
                print('Can\'t save image')

        e = discord.Embed(title="Voici ce que j'ai trouvé !", url=url, color=DEFAULT_COLOR)
        file = discord.File(temp_list_img.name, filename=temp_list_img.name)
        e.set_image(url="attachment://" + temp_list_img.name)
        await ctx.send(file=file, embed=e)
        os.remove(temp_list_img.name)
        driver.close()


def setup(bot):
    bot.add_cog(CheckPrice(bot))
