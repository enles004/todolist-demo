import requests
from celery import Celery

from handlers.email import send_register_notify_email, send_delete_project_notify_email

app = Celery('tasks', broker='pyamqp://guest@localhost//')


@app.task
def send_telegram(message):
    requests.get(
        f"https://api.telegram.org/bot6842966949:AAG36ZmSWGojw3ez0dcMLegInQ5rdw4lRpg/sendMessage?chat_id=1457896502"
        f"&text={message}")


@app.task
def send_mail_register(data):
    send_register_notify_email(data)


@app.task
def send_mail_delete(data):
    send_delete_project_notify_email(data)
