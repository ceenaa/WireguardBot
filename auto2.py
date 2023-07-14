import time
import sched
import gspread

import functions
import sheet

sa = gspread.service_account(filename='keys.json')
sh = sa.open_by_key(sheet.sheet_id)
wks = sh.worksheet("Sheet1")
delay_time = 60 * 60 * 24


def auto(scheduler):
    scheduler.enter(delay_time, 1, auto, (scheduler,))
    conf_names = wks.col_values(3)
    days = wks.col_values(5)
    status = wks.col_values(6)

    for i in range(len(conf_names)):
        if conf_names[i] == "conf_name":
            continue
        if days[i] == "31" and status[i] == "1":
            functions.pause_user(conf_names[i])


def main():
    my_scheduler = sched.scheduler(time.time, time.sleep)
    my_scheduler.enter(1, 1, auto, (my_scheduler,))
    my_scheduler.run()
