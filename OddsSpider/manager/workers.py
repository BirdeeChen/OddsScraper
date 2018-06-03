from celery import Celery

app = Celery('OddsCrawler', broker = 'redis://127.0.0.1:6379/0', backend = 'redis://127.0.0.1:6379/1', include = ['tasks.sportterycn',])

app.conf.update(
    # CELERY_TIMEZONE = 'Asia/Shanghai',
    # CELERY_ENABLE_UTC = True,
    CELERY_ACCEPT_CONTENT = ['json'],
    CELERY_TASK_SERIALIZER = 'json',
    CELERY_RESULT_SERIALIZER = 'json',
)

if __name__ == '__main__':
    app.start()