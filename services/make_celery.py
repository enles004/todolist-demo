from celery import Celery

from config import broker_url, psql_url


def make_celery(app):
    celery = Celery(app.import_name, broker=broker_url, backend=psql_url)
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


