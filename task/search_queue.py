import time

import config
from app.scrapper import Rutracker

USER = config.get_secret("RUTR_USER")
PASS = config.get_secret("RUTR_PASS")

tracker = Rutracker(USER, PASS)

tracker.login()
time.sleep(3)
data = tracker.search('Мстители')
