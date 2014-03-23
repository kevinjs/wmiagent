#coding:utf-8
import win32serviceutil
import win32service
import win32event
import win32evtlogutil
import time
import traceback
from HttpServer import Handler
from HttpServer import ThreadedHTTPServer

class HttpServerManager(win32serviceutil.ServiceFramework):
    _svc_name_ = "agent_http_server"
    _svc_display_name_ = "agent_http_server"
    _http_server = None

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self._http_server = ThreadedHTTPServer(('0.0.0.0', 8655), Handler)
        print 'Service start.'
        
    def SvcDoRun(self):
        import servicemanager
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,servicemanager.PYS_SERVICE_STARTED,(self._svc_name_, ''))
        self._http_server.serve_forever()
        return

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self._http_server.stop()
        win32event.SetEvent(self.hWaitStop)
        print 'Service stop'
        return

if __name__=='__main__':
    win32serviceutil.HandleCommandLine(HttpServerManager)
