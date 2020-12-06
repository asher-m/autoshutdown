# -*- coding: utf-8 -*-
"""
Created on Sat Dec  5 14:18:25 2020

@author: asher
"""

import ctypes
import datetime as dt
import json
import os
import subprocess
import time

import psutil

# ctypes promtps:
MB_OK = 0x0
MB_OKCXL = 0x01
MB_YESNOCXL = 0x03
MB_YESNO = 0x04
MB_HELP = 0x4000

# ctypes icons:
ICON_EXLAIM = 0x30
ICON_INFO = 0x40
ICON_STOP = 0x10

# ctypes default buttons:
DEF_BUT1 = 0x000  # default to button 1
DEF_BUT2 = 0x100  # default to button 2, etc...
DEF_BUT3 = 0x200
DEF_BUT4 = 0x300

# ctypes responses:
ID_OK = 0
ID_CANCEL = 2
ID_ABORT = 3
ID_YES = 6
ID_NO = 7

badtimes = (  # badtimes[0] <= bad <= badtimes[-1]
    dt.time(0, 30),
    dt.time(4, 30)
)

shutdown = 'shutdown -s -t 60'
shutdown_abort = 'shutdown -a'

processfile = os.path.join(os.path.dirname(__file__), 'processes.json')


# Open halt process file:
with open(processfile, 'r') as fp:
    halt_processes = json.load(fp)


def running_processes():
    """Get running processes."""
    return {proc.name() for proc in psutil.process_iter()}


def halt():
    """Check if any halt processes are active."""
    return any([(i in halt_processes) for i in running_processes()])


def main():
    """Wait for shutdown time, check if okay then shutdown."""
    # Wait until it's a bad time:
    now = dt.datetime.now()
    if not badtimes[0] <= now.time() <= badtimes[-1]:
        if now.time() < badtimes[0]:
            # Sleep until later today (case after midnight before bedtime):
            sleeptime = (dt.datetime.combine(dt.date.today(), badtimes[0]) -
                         dt.datetime.combine(dt.date.today(), now.time())).total_seconds()
        else:  # now.time() > badtimes[-1]:
            badtime_tomorrow = dt.datetime.combine(
                now + dt.timedelta(days=1),
                badtimes[0]
            )
            # Sleep until tomorrow's bedtime (ie., after midnight):
            sleeptime = (badtime_tomorrow - now).total_seconds()

        # Sleep for that time...
        print(f'Sleeping for {sleeptime} seconds...')
        time.sleep(sleeptime)

    while True:
        # Check if it's time to shutdown:
        while halt() is True:
            print('Shutdown-halting process open.  Waiting...')
            time.sleep(1.)

        # Then start shutdown clock:
        print('Trying shutdown...')
        subprocess.run(shutdown.split())

        # Ask if the user wants a delay:
        response = ctypes.windll.user32.MessageBoxW(
            None,
            "Shutdown scheduled in 60 seconds.\t\t\t\t\n\nSnooze for 10 minutes?",
            "Self Controller Improved",
            MB_YESNO | ICON_INFO | DEF_BUT2
        )
        if response == ID_YES:
            subprocess.run(shutdown_abort.split())
            print(
                'User requested snooze.  Sleeping for another 600 seconds for snooze...'
            )
            time.sleep(600)
        else:
            print('Shutdown not aborted, closing...')
            break


if __name__ == '__main__':
    main()
