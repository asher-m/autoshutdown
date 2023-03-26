# -*- coding: utf-8 -*-
"""
Created on Sat Dec  5 14:18:25 2020

@author: asher
"""

import datetime
import json
import os
import re
import subprocess
import time

import psutil


shutdown = r'shutdown -s -t {}'


def main():
    """Wait for shutdown time, check if okay then shutdown."""
    # Wait until it's a bad time:
    now = datetime.datetime.now()

    if bedtime <= now <= wuptime:
        sleeptime = 0
    else:
        sleeptime = (bedtime - now).total_seconds()

    print(f'Sleeping for {int(sleeptime)} seconds...')
    time.sleep(sleeptime)

    if delay() is True:
        wait_for_shutdown = 30 * 60  # seconds
        print(f'Got delay, setting shutdown in {int(wait_for_shutdown / 60):d}'
              ' minutes...')
    else:
        wait_for_shutdown = 3 * 60  # seconds
        print(f'Got no delay, setting shutdown in {int(wait_for_shutdown / 60):d}'
              ' minutes...')
    subprocess.run(shutdown.format(wait_for_shutdown).split())

    input('Press ENTER to close...')


def get_times(timelines):
    """Decide end and beginning times for system usage.

    Works by:
    1: Beg is today if beg >= now, else tomorrow.
    2: End is on the day of beg if end <= beg, else it is the day before."""
    today = datetime.datetime.now().date()
    tomorrow = today + datetime.timedelta(days=1)
    now = datetime.datetime.now()

    m_beg = re.match(r'beg:(\d{1,2}):(\d{1,2})', timelines[1])
    t_beg = datetime.time(int(m_beg.group(1)), int(m_beg.group(2)))
    m_end = re.match(r'end:(\d{1,2}):(\d{1,2})', timelines[0])
    t_end = datetime.time(int(m_end.group(1)), int(m_end.group(2)))

    # decide day of wuptime
    if datetime.datetime.combine(today, t_beg) >= now:
        beg = datetime.datetime.combine(today, t_beg)
    else:
        beg = datetime.datetime.combine(tomorrow, t_beg)

    # decide day of bedtime
    if datetime.datetime.combine(beg.date(), t_end) <= beg:
        end = datetime.datetime.combine(beg.date(), t_end)
    else:
        end = datetime.datetime.combine(beg.date() - datetime.timedelta(days=1), t_end)

    return end, beg


def get_processes(processlines):
    """Get processes in process file lines.

    Make them lowercase to compare to running processes."""
    return {p.lower().strip() for p in processlines}


def get_processes_running():
    """Get running processes.

    Make them lowercase to compare to processes in process file."""
    return {proc.name().lower() for proc in psutil.process_iter()}


def delay():
    """Check if any halt processes are active."""
    return any([(p in processes) for p in get_processes_running()])


if __name__ == '__main__':
    with open(os.path.join(os.path.dirname(__file__), 'times.txt'), 'r') as fp:
        bedtime, wuptime = get_times(fp.readlines())

    with open(os.path.join(os.path.dirname(__file__), 'processes.txt'), 'r') as fp:
        processes = get_processes(fp.readlines())

    main()
