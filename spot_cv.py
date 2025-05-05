
import argparse
import os
import sys
import time
import cv2
import numpy as np
import bosdyn.client
import bosdyn.client.util
from bosdyn.client.image import ImageClient


from gpt_module import generate_function
from threading import Thread, Event
from bosdyn.client import create_standard_sdk

# Add import for new functions here
from SPOT_functions import authenticate_SPOT, stop_spot, power_off_spot, power_on_spot, move_spot_forward, move_spot_backward, move_spot_left, move_spot_right
import json

# import for text to speech, speech to text
from gtts import gTTS
import os
import pyttsx3

# STEPS FOR CV: 
    # 1. Progress --- downloaded required dependencies to run fetch.py function to capture images
    # 2. Next Step --- try CV function methods based on images captured 
        # a. First test: color reading
        # b. Second test: object detection
    # 3. Create a list of specific objects to recognize --- develop new plan

# Get SPOT credentials from environment variables
SPOT_USERNAME = os.getenv('SPOT_USERNAME')
SPOT_PASSWORD = os.getenv('SPOT_PASSWORD')
SPOT_IP = os.getenv('SPOT_IP')

if not all([SPOT_USERNAME, SPOT_PASSWORD, SPOT_IP]):
    raise ValueError("SPOT credentials not found in environment variables")

# Set up the robot with credentials
SDK = create_standard_sdk('SpotClient')
robot = SDK.create_robot(SPOT_IP)
robot.username = SPOT_USERNAME
robot.password = SPOT_PASSWORD
ROBOT = robot

def detect_red_object(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_red = np.array([0, 120, 70])
    upper_red = np.array([10, 255, 255])
    mask = cv2.inRange(hsv, lower_red, upper_red)
    return cv2.countNonZero(mask) > 500  # just a simple threshold

def main():
    # username = "admin"
    # password = "sh384s6nnk6q"
    
    print("Welcome to SPOT CV Testing! Before proceeding, let's set up the authentication...\n")
    # username = "admin"
    # password = "sh384s6nnk6q"

    # Authenticating SPOT for access
    # authenticate_SPOT = ROBOT.authenticate(username, password)
    if not authenticate_SPOT(robot=ROBOT):
        print("Cannot authenticate SPOT")
        return

    print("Reading images...\n")

    ## Read and detect image color: 
    cv_image = cv2.imread("TestingImage.png", cv2.IMREAD_COLOR)
    
    print("Outputting GUI window to show result...\n")
    ## Show result on separate window
    cv2.imshow("SPOT ROBOTICS: CV Testing", cv_image)


if __name__ == "main":
    if not main(sys.argv[1:]):
        sys.exit(1)



