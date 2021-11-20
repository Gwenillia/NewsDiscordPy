from src.consts import c

async def load_flux():
  req = c.execute('''
      SELECT * FROM flux
  ''')
  all_flux = req.fetchall()
  return all_flux
