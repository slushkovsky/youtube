import sys
import os
sys.path += [
    os.path.join(os.path.curdir, '')
]

from sys import stdout
from logging import getLogger, DEBUG, StreamHandler

from youtube_api.search.youtube import build_youtube
from youtube_api.discoverer.discoverer import Discoverer
from pymongo import MongoClient


log = getLogger()
log.setLevel(DEBUG)
log.addHandler(StreamHandler(stdout))


client = MongoClient()

yt = build_youtube()
d = Discoverer(yt, client.get_database('yt_platform'))

d.process_channel('UCkLW_DM_SDnOjKJ5YF7FzhQ')
