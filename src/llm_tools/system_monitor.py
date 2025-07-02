import time
import psutil
import threading
import platform

class SystemMonitor:
    def __init__(self, interval=0.5):
        self.interval = interval
        self.system_stats = []
        self.monitoring = False
        self.monitor_thread = None
        self.gpu_available = False
        try:
            import pynvml
            pynvml.nvmlInit()
            self.gpu_available = True
        except Exception:
            self.gpu_available = False

    def _monitor_system_loop(self):
        """Internal loop to continuously monitor system resources."""
        while self.monitoring:
            stats = {
                'timestamp': time.time(),
                'cpu_percent': psutil.cpu_percent(interval=None), # Non-blocking call
                'memory_percent': psutil.virtual_memory().percent,
                'memory_used_gb': psutil.virtual_memory().used / (1024**3)
            }
            
            if self.gpu_available:
                try:
                    import pynvml
                    handle = pynvml.nvmlDeviceGetHandleByIndex(0) # Assuming single GPU for simplicity
                    gpu_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                    stats['gpu_memory_used_gb'] = gpu_info.used / (1024**3)
                    stats['gpu_memory_total_gb'] = gpu_info.total / (1024**3)
                    stats['gpu_utilization'] = pynvml.nvmlDeviceGetUtilizationRates(handle).gpu
                except Exception:
                    # If pynvml fails during monitoring, just skip GPU stats for this sample
                    pass
                    
            self.system_stats.append(stats)
            time.sleep(self.interval)

    def start(self):
        """Starts the system monitoring in a separate thread."""
        self.system_stats = []
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_system_loop)
        self.monitor_thread.daemon = True # Allow main program to exit even if thread is running
        self.monitor_thread.start()

    def stop(self):
        """Stops the system monitoring thread and returns collected stats."""
        self.monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1) # Wait for thread to finish
        return self.system_stats

    @staticmethod
    def get_system_info():
        """Gathers static system information."""
        info = {
            'platform': platform.platform(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'total_memory_gb': psutil.virtual_memory().total / (1024**3),
            'cpu_count_physical': psutil.cpu_count(logical=False),
            'cpu_count_logical': psutil.cpu_count(logical=True)
        }
        try:
            import pynvml
            pynvml.nvmlInit()
            gpu_count = pynvml.nvmlDeviceGetCount()
            gpu_info = []
            for i in range(gpu_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                name = pynvml.nvmlDeviceGetName(handle).decode('utf-8')
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpu_info.append({
                    'index': i,
                    'name': name,
                    'memory_total_gb': memory_info.total / (1024**3),
                    'memory_free_gb': memory_info.free / (1024**3)
                })
            info['gpu_info'] = gpu_info
        except Exception:
            info['gpu_info'] = "Not available"
        return info