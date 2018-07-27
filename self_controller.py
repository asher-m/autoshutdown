#!/usr/bin/env python3
"""
A simple script to limit the user's abilities past a certain time of day.

Reads programs from a file.  Program names in this file can be used to:
    Halt shutdown: Computer will not shutdown or interfere with user if
        program is on this list.
    Shutdown machine: When a processes on no_prompt BUT NOT on halt_shutdown is
        found, a shutdown in 5 minutes is started.

'no_prompt' processes are processes that the user has already been asked about,
thus does not need to be prompted about again.

'halt_shutdown' processes are processes the user has designated to halt
shutdown.

Future functionality: When a window goes fullscreen, user is prompted if
that window should be banned or not once past time.
"""


import ctypes
import datetime
import json
import os
import subprocess
import sys
import time

import psutil
import win32com.client
import win32gui
import win32process

# ctypes promtps:
MB_OK = 0x0
MB_OKCXL = 0x01
MB_YESNOCXL = 0x03
MB_YESNO = 0x04
MB_HELP = 0x4000
ICON_EXLAIM = 0x30
ICON_INFO = 0x40
ICON_STOP = 0x10

# ctypes responses:
ID_OK = 0
ID_CANCEL = 2
ID_ABORT = 3
ID_YES = 6
ID_NO = 7

########################
# Times:
EARLIEST = datetime.time(8) # Hours
LATEST = datetime.time(23, 30)

########################
# Process list file:
F = 'prx_list.json'

Fdir = os.path.dirname(sys.argv[0])
F = os.path.join(Fdir, F)

# Make sure F exists:
if not os.path.exists(F):
    with open(F, 'w') as f:
        json.dump({'halt_shutdown':[], 'no_prompt':[]}, f)

# Open the process list, then initialize the globals, then close it:
with open(F, 'r') as f:
    raw_prx_list = json.load(f)
    halt_shutdown = raw_prx_list['halt_shutdown']
    no_prompt = raw_prx_list['no_prompt']



def halt_time(now):
    """ Determines whether ``now`` is within valid time limits, as
    EARLIEST < now < LATEST.

    :param now: time to test against
    :type now: instance of datetime.datetime or datetime.time
    :trype: ``True`` if time is legal, ``False`` if time is illegal
    """
    if isinstance(now, datetime.datetime):
        return EARLIEST < now.time() < LATEST
    elif isinstance(now, datetime.time):
        return EARLIEST < now < LATEST
    else:
        raise TypeError('{} is not a datetime.datetime or'
                        ' datetime.time!'.format(now))

def halt_prx():
    """ Determines if there is a halting process active.
    
    :rtype: ``True`` if there is a halt process running,
            ``False`` if there is not.
    """
    return any([i in halt_shutdown for i in get_running_prx()])

def prompt(foreground):
    """ Asks user if ``foreground`` is a legal process.

    :param foreground: process to judge
    """
    response = ctypes.windll.user32.MessageBoxW(None,
                                                "Should {} halt shutdown?".\
                                                format(foreground),
                                                "Self Controller",
                                                MB_YESNO | ICON_INFO)
    # Get these from global space:
    global halt_shutdown, no_prompt
    if response == ID_YES: # Yes, append it to the good list:
        halt_shutdown.append(foreground)
    no_prompt.append(foreground)

def get_running_prx():
    wmi=win32com.client.GetObject('winmgmts:')
    return {p.Name for p in wmi.InstancesOf('win32_process')}

def prompted(foreground):
    if foreground not in no_prompt:
        prompt(foreground)

def shutdown():
    """ Tells the system to shutdown. """
    return subprocess.run(['shutdown', '-s', '-t', '120'])

def shutdown_query():
    """ Determines if the conditions to shutdown have been met. """
    foreground = active_window_process_name()
    now = datetime.datetime.now().time()
    # If there's no process stopping us from shutting down, and it'same
    # time to shutdown, do it:
    if not halt_prx() and not halt_time(now):
        return shutdown()
    # We didn't satisfy the conditions to begin with, so leave...
    return None

def active_window_process_name():
    """ Function to return the process name of the current executable.
    Amazingly taken from: https://stackoverflow.com/questions/14394513/
        win32gui-get-the-current-active-application-name
    """
    while True:
        try:
            pid = win32process.GetWindowThreadProcessId(win32gui.\
                                                        GetForegroundWindow())
            pname = psutil.Process(pid[-1]).name()
        except:
            pass
        else:
            return pname

def main():
    """ Main execution loop.
    
    While sleeping, (outside restriction time,) program checks every
    5 seconds for what the user is doing so it's possible to profile
    all applications the user is likely to use when inside restriction time.
    """
    # If we need to delay:
    if datetime.datetime.combine(datetime.date.today(), EARLIEST) < \
    datetime.datetime.now() < \
    datetime.datetime.combine(datetime.date.today(), LATEST):
        response = ctypes.windll.user32.MessageBoxW(None,
                                            "Waiting for shutdown...",
                                            "Self Controller",
                                            MB_OK | ICON_INFO)
        # While still time to delay:
        while datetime.datetime.now() < \
        datetime.datetime.combine(datetime.date.today(), LATEST):
            # Sleep for 5 seconds, then see if we've already profiled this
            # process:
            time.sleep(5)
            prompted(active_window_process_name())

    else:
        response = ctypes.windll.user32.MessageBoxW(None,
                                    "Past bedtime...",
                                    "Self Controller",
                                    MB_OK | ICON_INFO)

    # When in normal execution, check every 5 seconds:
    while True:
        time.sleep(5)
        response = shutdown_query()
        if response and response.returncode != 0:
            raise ValueError('Shutdown returned non-zero exit code: '
                               '{}'.format(response.returncode))
        elif response:
            break


try:
    main()
except Exception as e:
    print('WARNING: Exception caught:\n{}'.format(e))
finally:
    with open(F, 'w') as f:
        json.dump({'halt_shutdown':halt_shutdown, 'no_prompt':no_prompt},
                  f, indent=4, sort_keys=True)
