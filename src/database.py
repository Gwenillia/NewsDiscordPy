import asyncpg


class Database:
  def __init__(self, loop, user, password):
    self.user = user
    self.password = password
    loop.create_task(self.connect())

  async def connect(self):
    try:
      self.conn = await asyncpg.connect(user=self.user, password=self.password, host='127.0.0.1')
    except Exception as ex:
      print('error {0}:{1!r}'.format(type(ex).__name__, ex.args))

    db_exists = await self.conn.fetch('SELECT datname FROM pg_catalog.pg_database WHERE datname=\'arca_news\'')
    if not db_exists:
      await self.conn.fetch('CREATE DATABASE arca_news')
    await self.conn.close()

    self.conn = await asyncpg.connect(user=self.user, password=self.password, database='arca_news', host='127.0.0.1')
    await self.conn.fetch('''
      CREATE TABLE IF NOT EXISTS guild
      (
        ID SERIAL PRIMARY KEY NOT NULL,
        discord_guild_id BIGSERIAL NOT NULL,
        prefix VARCHAR(3) NOT NULL DEFAULT ';',
        joined_date TIMESTAMPTZ NOT NULL DEFAULT now()
      );
    ''')
    await self.conn.fetch('''
      CREATE TABLE IF NOT EXISTS flux
      (
        ID SERIAL NOT NULL,
        GUILD_ID BIGSERIAL NOT NULL,
        url VARCHAR(2083) NOT NULL,
        flux_name VARCHAR(40) NOT NULL,
        discord_channel_id BIGSERIAL NOT NULL,
        added_date TIMESTAMPTZ NOT NULL DEFAULT now(),
        UNIQUE (url, flux_name, discord_channel_id),
        CONSTRAINT flux_pk PRIMARY KEY (ID, GUILD_ID),
        CONSTRAINT flux_guild_fk FOREIGN KEY (GUILD_ID) REFERENCES guild(ID)
      );
    ''')
    await self.conn.fetch('''
      CREATE TABLE IF NOT EXISTS "user"
      (
        ID SERIAL PRIMARY KEY NOT NULL,
        discord_user_id BIGSERIAL NOT NULL
      );
    ''')
    await self.conn.fetch('''
      CREATE TABLE IF NOT EXISTS member
      (
        USER_ID SERIAL NOT NULL,
        GUILD_ID SERIAL NOT NULL,
        level SERIAL NOT NULL,
        xp SERIAL NOT NULL,
        CONSTRAINT member_pk PRIMARY KEY (USER_ID, GUILD_ID),
        CONSTRAINT member_user_fk FOREIGN KEY (USER_ID) REFERENCES "user"(ID),
        CONSTRAINT member_guild_fk FOREIGN KEY (GUILD_ID) REFERENCES guild(ID)
      );
    ''')

  async def fetch(self, sql, *args):
    return await self.conn.fetch(sql, *args)

  async def execute(self, sql, *args):
    return await self.conn.execute(sql, *args)
