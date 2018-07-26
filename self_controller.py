#!/usr/bin/env python3
"""
A simple script to limit the user's abilities past a certain time of day.

Reads programs from a file.  Program names in this file can be used to:
    Halt shutdown: Computer will not shutdown or interfere with user if
        program is on this list.
    Kill program: User will be notified that the program on kill list
        will be terminated in some ammount of time; program is then killed.

Future functionality: When a window goes fullscreen, user is prompted if
that window should be banned or not once past time.
"""


import ctypes
import datetime
import json
import psutil
import time
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

EARLIEST = datetime.time(7)
LATEST = datetime.time(15)

F = 'prx.json' # Note that no_prompt is a superset of halt_shutdown
# In other words, all items on halt_shutdown should be on no_prompt



def legal_time(now):
    """ Determines whether ``now`` is within valid time limits, as
    EARLIEST < now < LATEST.

    :param now: time to test against
    :type now: instance of datetime.datetime or datetime.time
    """
    if isinstance(now, datetime.datetime):
        return EARLIEST < now.time() < LATEST
    elif isinstance(now, datetime.time):
        return EARLIEST < now < LATEST
    else:
        raise TypeError('{} is not a datetime.datetime or'
                        ' datetime.time!'.format(now))


def legal_prx(foreground):
    """ Determines if ``foreground`` is a permitted process by reading
    permissible list from prx.json file.

    :param foreground: process to judge
    """
    with open(F, 'r') as f:
        halt_shutdown, _ = json.load(f) # First obj is halt_shutdown, second
        # obj is no_prompt
    return foreground in halt_shutdown


def prompt(foreground):
    """ Asks user if ``foreground`` is a legal process.

    :param foreground: process to judge
    """
    response = ctypes.windll.user32.MessageBoxW(None,
                                                "Is {} a legal program?".\
                                                format(foreground),
                                                "Self Controller",
                                                MB_YESNO | ICON_INFO)
    # Read file:
    with open(F, 'r') as f:
        halt_shutdown, no_prompt = json.load(f)
    if response == ID_YES: # If good, append it to the good list:
        halt_shutdown.append(foreground)
    no_prompt.append(foreground)
    # Write file:
    with open(F, 'w') as f:
        json.dump((halt_shutdown, no_prompt), f, indent=4, sort_keys=True)


def prompted(foreground):
    # Read file:
    with open(F, 'r') as f:    
        _, no_prompt = json.load(f)
    if foreground not in no_prompt:
        prompt(foreground)
    return True


def shutdown():
    """ Tells the system to shutdown. """
    print('SHUTTING DOWN')


def shutdown_query():
    """ Determines if the conditions to shutdown have been met. """
    foreground = active_window_process_name()
    now = datetime.datetime.now().time()
    # If all the conditions are met, shutdown:  (Note this is order-specific)
    if prompted(foreground) and not legal_prx(foreground)\
    and not legal_time(now):
        shutdown()


def active_window_process_name():
    """ Function to return the process name of the current executable.
    Amazingly taken from: https://stackoverflow.com/questions/14394513/
        win32gui-get-the-current-active-application-name
    """
    pid = win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow())
    return psutil.Process(pid[-1]).name()


def main():
    """ OOGGITY BOOGITY """
    while True:
        time.sleep(3)
        shutdown_query()


main()


F.close()
