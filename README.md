# autoshutdown
When your self control fails, but you want to stay somewhat close to your schedule: autoshutdown will enforce a bedtime for you!

This script will wait 3 minutes past the end-of-day time to shutdown your PC while checking to ensure no important applications (as designated in `processes.txt`) are open.  If an important application is open, it will wait an additional 30 minutes before shutting down your PC, while using the Windows user shutdown interface to provide the necessary warnings to users to save and close their work.

## Configuration and Installation

### Setting end-of-day and start-of-day hours
The file `times.txt` contains two lines and is formatted as:
<pre>
end:<i>hh</i>:<i>mm</i>
beg:<i>hh</i>:<i>mm</i>
</pre>

This script comes prefilled with end-of-day and start-of-day hours as 23:30 and 04:30, respectively.  Modify `times.txt` to change these times to your wishes.

### Delaying shutdown when an important application is open
The file `processes.txt` contains the text name of processes to trigger a 30-minute delay in shutdown.  This is to give the user time to save and close their work, or, perhaps more likely, to finish and close their game, (be it Dota, Factorio, or anything else.)  This list of processes can be modified by adding or removing lines from `processes.txt`.  The file comes prefilled with entries for games I play often, including:
<pre>
dota2.exe
factorio.exe
r5apex.exe
rdr2.exe
subnautica.exe
</pre>

**Note:** Process names must be added as **all-lowercase.**  Alphabetization is optional, but for long lists makes finding what you're looking for easier.  Alternatively, ctrl+f through the list.

### Installation
autoshutdown can be run in any base Python, approximately 3.6+.  Accordingly, I recommend installation in the following way:  Create a shortcut for Windows targeting your pythonw.exe (the windowless Python console executable) that runs `autoshutdown.py` from this directory.  Place this shortcut in your Start Menu's Startup folder.
1. Navigate to your Python installation directory.  I use miniconda but installed in a non-standard location, so I navigate to `%userprofile%/.miniconda3/`.
2. Find pythonw.exe.  Right click then select Copy.
3. Navigate to `%AppData%\Microsoft\Windows\Start Menu\Programs\Startup\`, Right Click and select Paste Shortcut.
4. Right Click on the shortcut and select Properties.  Modify the shortcut such that the Target line starts with the executable (path to pythonw.exe), followed by a space, followed by the path to `autoshutdown.py`.

For example, the target line in my shortcut is as follows: `%userprofile%\.miniconda3\pythonw.exe %userprofile%/Git/autoshutdown/self-controller.py`.  Microsoft has finally decided to allow forward slashes as valid path tokens, so fordward and backslashes shouldn't (and do not) make a difference.

If you'd like to test the script and the shortcut, you can change the target of the shortcut from pythonw.exe to python.exe, which will spawn a python console and print some debugging information, (normally suppressed by lack of reporting console.)

The script will handle the rest, and you can continue using your PC in peace while the script idles in the background, waiting to warn you to go to bed.  In terms of resource utilization, the script literally sleeps until needed, and python and Windows have evidently made this more efficient as the sleeping processes uses only (only!?) 7 MB of RAM, (emphasis added because a similar but efficiently designed executable from compiled C/C++ might use a few KB of RAM.  Nonetheless, with 32 GB of RAM, I can't be bothered to care about 7 MB.)
