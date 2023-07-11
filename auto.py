import os
import sched
import time

from dotenv import load_dotenv

import functions
import sheet

load_dotenv()
max_transfer = float(os.getenv("MAX_TRANSFER"))

global delay_time


def do_something(scheduler):
    scheduler.enter(delay_time, 1, do_something, (scheduler,))
    functions.reload()
    sheet.main()
    functions.export()
    for peer in functions.sortedPeer:
        if peer.active == 1 and peer.transfer >= max_transfer:
            functions.pause_user(peer.name)
        if peer.transfer < max_transfer:
            break


def auto(delay):
    global delay_time
    delay_time = delay
    my_scheduler = sched.scheduler(time.time, time.sleep)
    my_scheduler.enter(delay_time, 1, do_something, (my_scheduler,))
    my_scheduler.run()
