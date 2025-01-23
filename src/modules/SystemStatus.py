from asyncio.subprocess import Process

import psutil

class SystemStatus:
    pass

class CPU:
    def __init__(self):
        self.cpu_percent: float = 0
        self.cpu_percent_per_cpu: list[float] = []
    def getData(self):
        try:
            self.cpu_percent = psutil.cpu_percent(interval=0.5, percpu=True)
            self.cpu_percent_per_cpu = psutil.cpu_percent(interval=0.5)
        except Exception as e:
            pass
    def toJson(self):
        self.getData()
        return self.__dict__

class Memory:
    def __init__(self, memoryType: str):
        self.__memoryType = memoryType
        self.total = 0
        self.available = 0
        self.percent = 0
    def getData(self):
        if self.__memoryType == "virtual":
            memory = psutil.virtual_memory()
        else:
            memory = psutil.swap_memory()
        self.total = memory.total
        self.available = memory.available
        self.percent = memory.percent
    def toJson(self):
        self.getData()
        return self.__dict__
    
class Disk:
    def __init__(self, mountPoint: str):
        self.total = 0
        self.used = 0
        self.free = 0
        self.percent = 0
        self.mountPoint = mountPoint
    def getData(self):
        disk = psutil.disk_usage(self.mountPoint)
        self.total = disk.total
        self.free = disk.free
        self.used = disk.used
        self.percent = disk.percent
    def toJson(self):
        self.getData()
        return self.__dict__
    
class NetworkInterfaces:
    def __init__(self):
        self.interfaces = {}
    def getData(self):
        network = psutil.net_io_counters(pernic=True, nowrap=True)
        for i in network.keys():
            self.interfaces[i] = network[i]._asdict()
    def toJson(self):
        self.getData()
        return self.interfaces

class Processes:
    class Process:
        def __init__(self, name, command, pid, percent):
            self.name = name
            self.command = command
            self.pid = pid
            self.percent = percent
        def toJson(self):
            return self.__dict__
    def __init__(self):
        self.CPU_Top_10_Processes: list[Processes.Process] = []
        self.Memory_Top_10_Processes: list[Processes.Process] = []
    def getData(self):
        processes = list(psutil.process_iter())
        self.CPU_Top_10_Processes = sorted(list(map(lambda x : 
                    Processes.Process(x.name(), " ".join(x.cmdline()), x.pid, x.cpu_percent()), processes)),
                    key=lambda x : x.percent, reverse=True)[:10]
        self.Memory_Top_10_Processes = sorted(list(map(lambda x :
                    Processes.Process(x.name(), " ".join(x.cmdline()), x.pid, x.memory_percent()), processes)),
                    key=lambda x : x.percent, reverse=True)[:10]
    def toJson(self):
        self.getData()
        return {
            "cpu_top_10": self.CPU_Top_10_Processes,
            "memory_top_10": self.Memory_Top_10_Processes
        }

p = Processes()
print(p.toJson())