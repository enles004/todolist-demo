import time
from datetime import datetime

from tasks import send_telegram

while(True):
    e = int(time.time()) / 1000
    if e % 2 == 0:
        send_telegram.delay(f"Xin chao, bay gio la {datetime.now()}")
