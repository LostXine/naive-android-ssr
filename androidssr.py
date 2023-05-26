from adb_shell.adb_device import AdbDeviceTcp
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
        self.shell_pipe = AdbDeviceTcp(cfg['adb_ip'], cfg['adb_port'], default_transport_timeout_s=cfg['adb_timeout'])
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
        if self.shell_pipe.connect(): 
            self.shell('pkill -2 screenrecord')
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
