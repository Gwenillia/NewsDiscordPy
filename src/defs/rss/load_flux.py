async def load_flux(bot):
  req = await bot.db.fetch('''
      SELECT * FROM flux
  ''')
  all_flux = req
  return all_flux
