from asyncio.subprocess import Process

import psutil

class SystemStatus:
    def __init__(self):
        self.CPU = CPU()
        self.MemoryVirtual = Memory('virtual')
        self.MemorySwap = Memory('swap')
        self.Disks = Disks()
        self.NetworkInterfaces = NetworkInterfaces()
        self.Processes = Processes()
    def toJson(self):
        return {
            "CPU": self.CPU,
            "Memory": {
                "VirtualMemory": self.MemoryVirtual,
                "SwapMemory": self.MemorySwap
            },
            "Disks": self.Disks,
            "NetworkInterfaces": self.NetworkInterfaces,
            "Processes": self.Processes
        }
        

class CPU:
    def __init__(self):
        self.cpu_percent: float = 0
        self.cpu_percent_per_cpu: list[float] = []
    def getData(self):
        try:
            self.cpu_percent_per_cpu = psutil.cpu_percent(interval=0.5, percpu=True)
            self.cpu_percent = psutil.cpu_percent(interval=0.5)
        except Exception as e:
            pass
    def toJson(self):
        self.getData()
        return self.__dict__

class Memory:
    def __init__(self, memoryType: str):
        self.__memoryType__ = memoryType
        self.total = 0
        self.available = 0
        self.percent = 0
    def getData(self):
        try:
            if self.__memoryType__ == "virtual":
                memory = psutil.virtual_memory()
            else:
                memory = psutil.swap_memory()
            self.total = memory.total
            self.available = memory.available
            self.percent = memory.percent
        except Exception as e:
            pass
    def toJson(self):
        self.getData()
        return self.__dict__

class Disks:
    def __init__(self):
        self.disks : list[Disk] = []
    def getData(self):
        try:
            self.disks = list(map(lambda x : Disk(x.mountpoint), psutil.disk_partitions()))
        except Exception as e:
            pass
    def toJson(self):
        self.getData()
        return self.disks

class Disk:
    def __init__(self, mountPoint: str):
        self.total = 0
        self.used = 0
        self.free = 0
        self.percent = 0
        self.mountPoint = mountPoint
    def getData(self):
        try:
            disk = psutil.disk_usage(self.mountPoint)
            self.total = disk.total
            self.free = disk.free
            self.used = disk.used
            self.percent = disk.percent
        except Exception as e:
            pass
    def toJson(self):
        self.getData()
        return self.__dict__
    
class NetworkInterfaces:
    def __init__(self):
        self.interfaces = {}
    def getData(self):
        try:
            network = psutil.net_io_counters(pernic=True, nowrap=True)
            for i in network.keys():
                self.interfaces[i] = network[i]._asdict()
        except Exception as e:
            pass
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
        while True:
            try:
                processes = list(psutil.process_iter())
                self.CPU_Top_10_Processes = sorted(
                    list(map(lambda x : Processes.Process(x.name(), " ".join(x.cmdline()), x.pid, x.cpu_percent()), processes)),
                    key=lambda x : x.percent, reverse=True)[:20]
                self.Memory_Top_10_Processes = sorted(
                    list(map(lambda x : Processes.Process(x.name(), " ".join(x.cmdline()), x.pid, x.memory_percent()), processes)),
                    key=lambda x : x.percent, reverse=True)[:20]
                break
            except Exception as e:
                continue
    def toJson(self):
        self.getData()
        return {
            "cpu_top_10": self.CPU_Top_10_Processes,
            "memory_top_10": self.Memory_Top_10_Processes
        }