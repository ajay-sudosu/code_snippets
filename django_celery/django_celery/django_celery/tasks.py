from django_celery.celery import app

@app.task
def add(x, y):
    x = x
    y = y
    return x + y
