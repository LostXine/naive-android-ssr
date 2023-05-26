from adb_shell.adb_device import AdbDeviceTcp, AdbDeviceUsb
from adb_shell.auth.sign_pythonrsa import PythonRSASigner
import time
import threading
import av

class Wrapper:
    name = "<wrapped>"
    def __init__(self):
        self._fh = bytearray()
        self.should_close = False
    
    def write(self, bytes):
        self._fh.extend(bytes)

    def read(self, buf_size):
        while buf_size > len(self._fh) and not self.should_close:
            time.sleep(0.1)
        buf = bytes(self._fh[:buf_size])
        del self._fh[:buf_size]
        return buf

class AndroidSSR:
    def __init__(self, cfg) -> None:
        if 'adb_ip' in cfg and 'adb_port' in cfg:
            self.shell_pipe = AdbDeviceTcp(cfg['adb_ip'], cfg['adb_port'], default_transport_timeout_s=cfg.get('adb_timeout', 10.0))
        else:
            self.shell_pipe = AdbDeviceUsb(default_transport_timeout_s=cfg.get('adb_timeout', 10.0))
        
        if 'adb_key' in cfg:
            adbkey = cfg['adb_key']
            with open(adbkey) as f:
                priv = f.read()
            with open(adbkey + '.pub') as f:
                pub = f.read()
            self.signer = PythonRSASigner(pub, priv)
            
        else:
            self.signer = None
        
        self.thread = threading.Thread(target=AndroidSSR._recvloop, args=(self,))
        self.dec_thread = threading.Thread(target=AndroidSSR._decloop, args=(self,))
        self.wp = Wrapper()

        self.frame_buf = None
        self.should_close = False
        
        self.stream_cmd = 'screenrecord --output-format=h264'
        if 'bitrate' in cfg:
            self.stream_cmd += f' --bit-rate={cfg["bitrate"]}'
        if 'size' in cfg:
            self.stream_cmd += f' --size {cfg["size"][0]}x{cfg["size"][1]}'
        self.stream_cmd += ' -'
        print(self.stream_cmd)
        
    
    def __enter__(self):
        if self.connect():
            return self
        else:
            return None
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def connect(self):
        if self.shell_pipe.connect([] if self.signer is None else [self.signer]): 
            self.thread.start() 
            self.dec_thread.start()
            return True
        else:
            print('Failed to connect to the device')
            return False
    
    def _decloop(self):
        with av.open(self.wp, format="h264", mode='r') as container:
            while True:
                for packet in container.demux():
                    if packet.size == 0:
                        continue
                    try:
                        for frame in packet.decode():
                            self.frame_buf = frame.to_ndarray(format='bgr24')
                    except av.error.InvalidDataError:
                        print('av.error.InvalidDataError')
                if self.wp.should_close:
                    break
            
    def _recvloop(self):
        self.shell('pkill -2 screenrecord')
        for data in self.shell_pipe.streaming_shell(self.stream_cmd, decode=False):
            self.wp.write(data)
            if self.wp.should_close:
                self.shell('pkill -2 screenrecord')
                break

    def get_frame(self):
        return self.frame_buf
    
    def shell(self, cmd):
        return self.shell_pipe.shell(cmd)
    
    def close(self):
        self.wp.should_close = True
        self.thread.join()
        self.dec_thread.join()
        self.shell('exit')
        self.wp.should_close = False
