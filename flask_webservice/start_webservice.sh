su -m myuser -c "redis-server > redis.log 2>&1 &"
su -m myuser -c "celery worker -A celery_worker.celery --concurrency=1 > celery.log 2>&1 &"
su -m myuser -c "python manage.py > flask.log 2>&1 &"