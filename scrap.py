import time

from app.scrapper import Rutracker

USER = ""
PASS = ""

tracker = Rutracker(USER, PASS)

tracker.login()
time.sleep(3)
tracker.search('Мстители')
