# self-controller
When your self control fails...

A simple script that shuts down your machine if you're not busy and it's past your bedtime.

This works by running in the 'background' when outside of the user's defined bedtime.  The script finds the executable of the active window every 5 seconds; if the active process has not been profiled before, the user is prompted as to whether this process should be allowed to keep the machine awake inside bedtime hours.  These data are stored in the prx_list.json file included with the script.

When inside the user's bedtime, the script compares the list of processes on the machine to what processes are defined in the prx_list.json file to halt shutdown.  If no 'halting' processes are running, the machine will shut down.

This script was intended to be run on Windows via Python's headless interface, (pythonw.exe.)  It was developed for Python3, though will likely work with Python2.7 as well.

The included process list is an example of what one may have in that list.

## Dependencies
### Non-standard dependencies:
* psutil
* win32com.client
* win32gui
* win32process

### Standard dependencies:
* ctypes
* datetime
* json
* os
* subprocess
* sys
* time
