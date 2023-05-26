# naive-android-ssr
Naive Android Screen Stream Reader, this project decodes Android screenrecord stream to OpenCV via ADB. Written in Python.

## Requirements
### PC
- Python >= 3.6
```
pip3 install adb-shell av opencv-python
```
Install `adb-shell[usb]` if you want to connect via USB.
```
pip3 install adb-shell[usb]
```

- A system that is strong enough to decode H264 stream.

### Android Phone/Simulator
- Android >= 4.4

## Run
1. Check your config file.
```
# This is the json file for MuMu 12 Simulator
{
    "adb_ip": "127.0.0.1",
    "adb_port": 7555, # usually this should be 5555 on other devices / simulators
    "adb_key": "mykey", # required by the real phone, optional for simulator. Use `keygen.py` to gen your key.
    "adb_timeout": 10.0,
    "size": [960, 540], # optional
    "bitrate": "4M" # optional
}
```
2. Launch the code using a config file:
```
python3 main.py mumu12.json
```
Wait several seconds for the decoder to receive enough data, then a opencv window will pop up.

You may need to allow the connection on your phone when connecting for the first time.

3. Press Enter or ESC to quit.

## Troubleshooting
1. On windows, when connecting to a phone, an error raised as `usb1.USBErrorAccess: LIBUSB_ERROR_ACCESS [-3]`. According to [this issue](https://github.com/JeffLIrion/adb_shell/issues/212), kill all adb procs will solve the problem.
```
taskkill /F /IM adb.exe
```

## Acknowledgment
This project is built on [adb-shell](https://github.com/JeffLIrion/adb_shell) and [PyAV](https://github.com/PyAV-Org/PyAV). I would like to thank all the authors for their wonderful works. Meanwhile, I learned a lot from this [post](https://stackoverflow.com/questions/62759863/how-to-use-pyav-or-opencv-to-decode-a-live-stream-of-raw-h-264-data).


