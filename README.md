#wmiagent

====

A Windows monitor agent. Fetch data by using WMI(Windows Management Instrumentation).

##Requirement:
1. Install WMI Administrative Tools
2. Install Python Win32 Extension
3. Install Python WMI

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
