import os
import sched
import time

from dotenv import load_dotenv

import functions
import sheet

sa = gspread.service_account(filename='keys.json')
sh = sa.open_by_key(sheet.sheet_id)
wks = sh.worksheet("Sheet1")

global delay_time


def do_something(scheduler):
    scheduler.enter(delay_time, 1, do_something, (scheduler,))
    functions.reload()
    sheet.main()
    functions.export()
    data_limits = wks.col_values(9)
    names = wks.col_values(3)
    status = wks.col_values(6)

    for i in range(1, len(names)):
        if status[i] == "0":
            continue
        if names[i] not in functions.peerMap.keys():
            continue
        if data_limits[i] == "0":
            continue
        if functions.peerMap[names[i]].transfer >= int(data_limits[i]):
            functions.pause_user(names[i])


def auto(delay):
    global delay_time
    delay_time = delay
    my_scheduler = sched.scheduler(time.time, time.sleep)
    my_scheduler.enter(delay_time, 1, do_something, (my_scheduler,))
    my_scheduler.run()
