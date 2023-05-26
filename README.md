# naive-android-ssr
Naive Android Screen Stream Reader, this project decodes Android screenrecord stream to OpenCV via TCP. Written in Python.

### Requirements
#### PC
- Python >= 3.6
```
pip3 install adb-shell av opencv-python
```
- A system that is strong enough to decode H264 stream.

#### Android Phone/Simulator
- Android >= 4.4

### Run
1. Check your config file.
```
# This is the json file for MuMu 12 Simulator
{
    "adb_ip": "127.0.0.1",
    "adb_port": 7555, # usually this should be 5555 on other devices / simulators
    "adb_timeout": 9.0,
    "size": [960, 540], # optional
    "bitrate": "4M" # optional
}
```
2. Launch the code:
```
python3 main.py mumu-config.json
```

### Contact me
* (Recommended) New issue 
* Email: lostxine@gmail.com
