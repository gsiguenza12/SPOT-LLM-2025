import os
import time
import socket
import subprocess
import cv2
import base64
import sys
import traceback
# from wormholelite import CameraVideo
# from websocket import create_connection
from gpt_module import generate_function
# from ai_pipeline.input_delegator import delegate_input
# from ai_pipeline.recognize_speech import listen_for_keyword
# from ai_pipeline.bot_handler import playAudio

# def start(spot):
#     playAudio(delegate_input(listen_for_keyword(), spot))

ROBOT_IP = "192.168.80.3" #['ROBOT_IP']
SPOT_USERNAME = "admin" #['SPOT_USERNAME']
SPOT_PASSWORD = "sh384s6nnk6q" #['SPOT_PASSWORD']

def main():
    # if True:
    from spot_controller import SpotController
    with SpotController(username=SPOT_USERNAME, password=SPOT_PASSWORD, robot_ip=ROBOT_IP) as spot:
        globals()["spot_global"] = spot
        # ws = create_connection("ws://localhost:8001/", ping_timeout=None)
        # ws.send("Hello, World")
        # cam = CameraVideo(0, max_fps=1, height=360, width=480)
        print("Starting")
        while True:
            try:
                # cmd =  ws.recv()
                if cmd == "[PAYLOAD]":
                    with open("/tmp/payload.py", "w+") as f:
                        f.seek(0)
                        f.truncate()
                        f.write(ws.recv())
                    try:
                        process = subprocess.Popen(["python3", "/tmp/payload.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                        for line in process.stdout:
                            ws.send(line.strip())
                        for line in process.stderr:
                            ws.send(line.strip())
                        process.wait()
                    except Exception as e:
                        ws.send(f"Error executing command: {e}")
                    ws.send("[EOL]")
                    continue
                res = eval(cmd)
                if res:
                    ws.send(str(res))
                else:
                    ws.send("None") 
            except Exception as e:
                print(traceback.format_exc())
                ws.send(str(e))


if __name__ == '__main__':
    main()

import time
time.sleep(50)
