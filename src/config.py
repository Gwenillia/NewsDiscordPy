class Config:
  def __init__(self, cfg):
    self.bot_token = cfg['bot_token']
    self.postgresql_user = cfg['postgresql_user']
    self.postgresql_password = cfg['postgresql_password']
    self.min_message_xp = cfg['min_message_xp']
    self.max_message_xp = cfg['max_message_xp']

class Colors:
  red = '\033[31m'
  reset = '\033[0m'