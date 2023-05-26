import argparse
import json
import time
from androidssr import AndroidSSR
import cv2

if __name__ == '__main__':
    parser = argparse.ArgumentParser('naive-android-ssr', 'Usage: python3 main.py config.json', 'This project decodes screen stream from an Android device into OpenCV frames.')
    parser.add_argument('config', type=str, default='mumu-config.json', help='config file in jsom')
    arg = parser.parse_args()
    
    with open(arg.config, 'r') as f:
        cfg = json.load(f)
    print(cfg)
    
    with AndroidSSR(cfg) as assr:
        print('Press ESC or Enter to exit.')
        while True:
            img = assr.get_frame()
            if img is None:
                time.sleep(0.1)
                continue
            cv2.imshow('Frame', img)
            c = cv2.waitKey(10) & 0xff
            if c in [13, 27]:
                break
        cv2.destroyAllWindows()
