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
    """Decide bedtime and wuptime from timelines.

    Works by:
    1: Look if wuptime can mean today (ie., wuptime >= now) it is, else tomorrow.
    2: If bedtime on the day of wuptime is <= wuptime, it is, else it is the day before."""
    today = datetime.datetime.now().date()
    tomorrow = today + datetime.timedelta(days=1)
    now = datetime.datetime.now()
    # decide day of wuptime
    m_wuptime = re.match(r'wuptime:(\d{1,2}):(\d{1,2})', timelines[1])
    t_wuptime = datetime.time(int(m_wuptime.group(1)), int(m_wuptime.group(2)))
    if datetime.datetime.combine(today, t_wuptime) >= now:
        wuptime = datetime.datetime.combine(today, t_wuptime)
    else:
        wuptime = datetime.datetime.combine(tomorrow, t_wuptime)

    # decide day of bedtime
    m_bedtime = re.match(r'bedtime:(\d{1,2}):(\d{1,2})', timelines[0])
    t_bedtime = datetime.time(int(m_bedtime.group(1)), int(m_bedtime.group(2)))

    if datetime.datetime.combine(wuptime.date(), t_bedtime) <= wuptime:
        bedtime = datetime.datetime.combine(wuptime.date(), t_bedtime)
    else:
        bedtime = datetime.datetime.combine(
            wuptime.date() - datetime.timedelta(days=1), t_bedtime)

    return bedtime, wuptime


def get_processes(processlines):
    """Get processes in process file lines.

    Make them lowercase to compare to running processes."""
    return {p.lower() for p in processlines}


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
