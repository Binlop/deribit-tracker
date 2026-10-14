from celery import Celery
from celery.schedules import schedule

from core.config import Settings, settings


def create_celery_app(settings: Settings) -> Celery:
    app = Celery(
        "prices",
        broker=settings.CELERY_BROKER_URL,
        backend=settings.CELERY_RESULT_BACKEND,
        include=["apps.deribit.tasks"],
    )
    app.conf.timezone = "UTC"
    app.conf.beat_schedule = {
        "fetch-index-prices": {
            "task": "apps.deribit.tasks.deribit_price_task",
            "schedule": schedule(run_every=settings.FETCH_INTERVAL_SECONDS),
        },
    }
    return app


celery_app = create_celery_app(settings)