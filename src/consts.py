import time

import pytz

date = time.time()
titles = []
TEMP_IMG = "temp-image{}.jpg"

DEFAULT_COLOR = 0x2b41ff
FIELD_NAMES = []
TZINFOS = {
  'PDT': pytz.timezone('US/Pacific'),
  '+0200': pytz.timezone('Africa/Cairo')
}
