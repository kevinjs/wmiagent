#wmiagent

A Windows monitor agent. Fetch data by using WMI(Windows Management Instrumentation).

##Requirement:
1. [WMI Administrative Tools](http://www.microsoft.com/en-us/download/details.aspx?id=24045)
2. [Python Win32 Extension](http://sourceforge.net/projects/pywin32/)
3. [Python WMI](https://pypi.python.org/pypi/WMI)

##Usage:

###1. Start Polling task
    python PollManager.py install
    python PollManager.py start

###2. Start Http Service
    python HttpServerManager.py install
    python HttpServerManager.py start

Then, you can see and manage them in Windows Server Manager.

###3. Stop Polling task
    python PollManager.py stop

###4. Stop Http Service
    python HttpServerManager.py stop

Edit by Kevin Shaw dysj4099@gmail.com
