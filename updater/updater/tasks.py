from celery.schedules import crontab
from celery.decorators import periodic_task

from pymongo import MongoClient

import sys
sys.path.insert(0, '../')
from YtLocalStore import YtLocalStore

@periodic_task(run_every=(crontab(minute='*/15')))
def yt_update_info():
    client = MongoClient()
    st = YtLocalStore(client.youtube)
    st.update()
    print("TASK DONE")
    