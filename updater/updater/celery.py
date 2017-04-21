from celery import Celery

app = Celery('updater',
             broker='mongodb://localhost:27017/celerydb',
             backend='mongodb://localhost:27017/celery_report',
             include=['updater.tasks'])

if __name__ == '__main__':
    app.start()