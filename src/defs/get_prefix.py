async def get_prefix(bot, message):
  req = await bot.db.fetch('SELECT EXISTS(SELECT 1 FROM guild WHERE discord_guild_id = $1)', message.guild.id)
  res = req[0][0]
  if res is False:
    await bot.db.execute('INSERT INTO guild (discord_guild_id, prefix) SELECT $1, $2 ON CONFLICT DO NOTHING',
                         message.guild.id, ";")
  else:
    req = await bot.db.fetch('SELECT prefix FROM guild WHERE discord_guild_id = $1', message.guild.id)
    res = req[0][0]
    prefix = str(res)
    return prefix
