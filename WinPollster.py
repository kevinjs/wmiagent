import wmi
import os
import sys
import platform
import time
import traceback
import win32com.client as client

class WinPollster(object):
    _c = None
    _cs = None
    _os = None
    _pfu = None
    _com = None
    _obj = None

    hostname = None
    ipaddress = None
    def __init__(self):
        self._c = wmi.WMI()
        self._com = client.Dispatch("WbemScripting.SWbemRefresher")
        self._obj = client.GetObject("winmgmts:\\root\cimv2")
        self._cs = self._c.Win32_ComputerSystem()
        self._os = self._c.Win32_OperatingSystem()
        self._pfu = self._c.Win32_PageFileUsage()
        self.hostname = self._os[0].CSName

    def get_cpu(self):
        data_dict = {}
        cpu_usage_total = 0
        
        for cpu in self._c.Win32_Processor():
            device = cpu.DeviceID.lower()
            data_dict[device] = {'volume':float(cpu.LoadPercentage), 'unit':'%'}
            cpu_usage_total += float(cpu.LoadPercentage)

        data_dict['cpu'] = {'volume':cpu_usage_total/len(data_dict), 'unit':'%'}
        return {'data':data_dict, 'timestamp':time.asctime(time.localtime())}

    def get_mem(self):
        data_dict = {}
        data_dict["MemTotal"] = {'volume':float(self._cs[0].TotalPhysicalMemory) / (1024*1024), 'unit':'MB'}
        data_dict["MemFree"] = {'volume':float(self._os[0].FreePhysicalMemory)/1024, 'unit':'MB'}
        data_dict["Cached"] = {'volume':0, 'unit':'MB'}
        data_dict["Buffers"] = {'volume':0, 'unit':'MB'}
        data_dict["SwapTotal"] = {'volume':float(self._pfu[0].AllocatedBaseSize), 'unit':'MB'}
        data_dict["SwapFree"] = {'volume':float(self._pfu[0].AllocatedBaseSize - self._pfu[0].CurrentUsage), 'unit':'MB'}
        return {'data':data_dict, 'timestamp':time.asctime(time.localtime())}

    def get_disk(self):
        diskitems = self._com.AddEnum(self._obj, "Win32_PerfFormattedData_PerfDisk_LogicalDisk").objectSet

        data_dict = {}
        data_dict['total_available'] = 0
        data_dict['total_capacity'] = 0
        data_dict['total_free'] = 0

        #  DriveType=3 : "Local Disk",
        for disk in self._c.Win32_LogicalDisk (DriveType=3):
            data_dict['total_available'] += round(float(disk.FreeSpace) / (1024*1024*1024), 2)
            data_dict['total_capacity'] += round(float(disk.Size) / (1024*1024*1024), 2)
            data_dict['total_free'] += round(float(disk.FreeSpace) / (1024*1024*1024), 2)

            dev_tmp = {}
            dev_tmp['dev'] = disk.DeviceID
            dev_tmp['available'] = {'volume':round(float(disk.FreeSpace) / (1024*1024*1024), 2), 'unit':'GB'}
            dev_tmp['capacity'] = {'volume':round(float(disk.Size) / (1024*1024*1024), 2), 'unit':'GB'}
            dev_tmp['free'] = {'volume':round(float(disk.FreeSpace) / (1024*1024*1024), 2), 'unit':'GB'}
            dev_tmp['fstype'] = disk.FileSystem
            dev_tmp['mnt'] = ''
            dev_tmp['used'] = round(long(disk.FreeSpace) / long(disk.Size), 2)

            data_dict[disk.DeviceID] = dev_tmp

        self._com.Refresh()
        for item in diskitems:
            if item.Name in data_dict:
                data_dict[item.Name]['io_stat'] = {}
                data_dict[item.Name]['io_stat']['r/s'] = {'volume':float(item.DiskReadsPerSec), 'unit':''}
                data_dict[item.Name]['io_stat']['w/s'] = {'volume':float(item.DiskWritesPerSec), 'unit':''}
                data_dict[item.Name]['io_stat']['rkB/s'] = {'volume':(float(item.DiskReadBytesPerSec) / 1024), 'unit':'KB/s'}
                data_dict[item.Name]['io_stat']['wkB/s'] = {'volume':(float(item.DiskWriteBytesPerSec) / 1024), 'unit':'KB/s'}
        return {'data':data_dict, 'timestamp':time.asctime(time.localtime())}

    def get_net(self):
        items = self._com.AddEnum(self._obj, "Win32_PerfRawData_Tcpip_NetworkInterface").objectSet

        data_dict = {}
        interfaces = []
        for interface in self._c.Win32_NetworkAdapterConfiguration (IPEnabled=1):
            if interface.IPAddress[0]:
                self.ipaddress = interface.IPAddress[0]
            interfaces.append(interface.Description)

        net_bytes_in = 0
        net_bytes_out = 0
        net_pkts_in = 0
        net_pkts_out = 0
        
        self._com.Refresh()
        for item in items:
            if item.Name in interfaces:
                net_bytes_in += long(item.BytesReceivedPerSec)
                net_bytes_out += long(item.BytesSentPerSec)
                net_pkts_in += long(item.PacketsReceivedPerSec)
                net_pkts_out += long(item.PacketsSentPerSec)

        time.sleep(1)

        net_bytes_in_cur = 0
        net_bytes_out_cur = 0
        
        self._com.Refresh()
        for item in items:
            if item.Name in interfaces:
                net_bytes_in = long(item.BytesReceivedPerSec) - net_bytes_in
                net_bytes_in_cur += long(item.BytesReceivedPerSec)
                net_bytes_out = long(item.BytesSentPerSec) - net_bytes_out
                net_bytes_out_cur += long(item.BytesSentPerSec)
                net_pkts_in = long(item.PacketsReceivedPerSec) - net_pkts_in
                net_pkts_out = long(item.PacketsSentPerSec) - net_pkts_out

        data_dict['net_bytes_in'] = {'volume':net_bytes_in, 'unit':'B/s'}
        data_dict['net_bytes_in_sum'] = {'volume':net_bytes_in_cur, 'unit':'B'}
        data_dict['net_bytes_out'] = {'volume':net_bytes_out, 'unit':'B/s'}
        data_dict['net_bytes_out_sum'] = {'volume':net_bytes_out_cur, 'unit':'B'}
        data_dict['net_pkts_in'] = {'volume':net_pkts_in, 'unit':'p/s'}
        data_dict['net_pkts_out'] = {'volume':net_pkts_out, 'unit':'p/s'}

        return {'data':data_dict, 'timestamp':time.asctime(time.localtime())}

    def combine(self):
        combine_data = {}
        combine_data['data'] = {}
        combine_data['hostname'] = self.hostname
        try:
            combine_data['data']['CPUUsagePollster'] = self.get_cpu()
            combine_data['data']['DiskUsagePollster'] = self.get_disk()
            combine_data['data']['MemInfoPollster'] = self.get_mem()
            combine_data['data']['NetStatPollster'] = self.get_net()

            if self.ipaddress:
                combine_data['ip_address'] = self.ipaddress
            else:
                combine_data['ip_address'] = '127.0.0.1'
            combine_data['status'] = 'NORMAL'
        except Exception,err:
            print err
            print traceback.format_exc()
            combine_data['status'] = 'ERROR'
        finally:
            combine_data['timestamp'] = time.asctime(time.localtime()) 
            return combine_data

if __name__=='__main__':
    wp = WinPollster()
    print wp.combine()
    
    
