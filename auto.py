import sched
import time

import functions
import sheet
import gspread

sa = gspread.service_account(filename='keys.json')
sh = sa.open_by_key(sheet.sheet_id)
wks = sh.worksheet("Sheet1")

delay_time = 60 * 30


def do_something(scheduler):
    scheduler.enter(delay_time, 1, do_something, (scheduler,))
    try:
        functions.reload()
        sheet.main()
        functions.export()
        data_limits = wks.col_values(9)
        names = wks.col_values(3)
        status = wks.col_values(6)
        days = wks.col_values(5)

        for i in range(1, len(names)):
            if names[i] not in functions.peerMap.keys():
                continue
            if status[i] == "0":
                continue
            if days[i] == "31" and status[i] == "1":
                functions.pause_user(names[i])
            elif data_limits[i] == "0":
                continue
            elif functions.peerMap[names[i]].transfer >= float(data_limits[i]):
                functions.pause_user(names[i])
    except Exception as err:
        print(type(err).__name__ + " " + str(err))


def auto():
    my_scheduler = sched.scheduler(time.time, time.sleep)
    my_scheduler.enter(1, 1, do_something, (my_scheduler,))
    my_scheduler.run()
