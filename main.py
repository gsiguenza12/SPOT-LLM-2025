from gpt_module import generate_function
from threading import Thread, Event
from bosdyn.client import create_standard_sdk
from bosdyn.api import robot_state_pb2

# Add import for new functions here
from SPOT_functions import authenticate_SPOT, stop_spot, power_off_spot, power_on_spot, move_spot_forward, make_spot_stand
import json

# import for text to speech, speech to text
from gtts import gTTS
import os
import pyttsx3


COMMAND_LIST = {
    "power_on", 
    "power_off", 
    "move_spot_forward",
    # ADD move_spot_backward
    "stand",
    "stop",
    "quit"
    }

SDK = create_standard_sdk('SpotClient')   #create spot sdk
ROBOT = SDK.create_robot('192.168.80.3')


# to test
mytext = "Hello welcome to the spot llm program!"

# which language you want to convert
language = 'en'

# Passing the text and language to the engine,
# here we have marked slow=False. Which tells
# the module that the converted audio should
# have a high speed
myobj = gTTS(text=mytext, lang=language, slow=False)

# Saving the converted audio in a mp3 file named
# welcome
myobj.save("welcome.mp3")

# Playing the converted file
# os.system("start welcome.mp3")

def clean_tasks(threads, event):
    if(len(threads) == 0):
        return
    if(threads[0].is_alive):
        event.set()
        threads[0].join()
        event.clear()

def valid_function(function_name):
    if function_name not in COMMAND_LIST:
        raise Exception("Command is not registered as a function")

def check_gpt_response(gpt_completion):
    """
    Check if GPT's response is the expected function call
    """
    if(gpt_completion.choices[0].finish_reason != "tool_calls"):
        raise Exception("GPT response is not a function")
    gpt_function_name = gpt_completion.choices[0].message.tool_calls[0].function.name
    gpt_arguments = gpt_completion.choices[0].message.tool_calls[0].function.arguments
    valid_function(gpt_function_name)

def check_stop_or_quit(input_string, threads, event):
    if input_string in {"stop", "quit"}:
        clean_tasks(threads, event)
        stop_spot(ROBOT)
        if input_string == "quit":
            print("Quitting program")
            return True
    return False

def task(event, function_name, function_arguments):
    print("Attempting to run the function " + function_name)
    # get the current state of the robot
    robot_state = ROBOT.get_state();
    if(function_name == "move_spot_forward"):
        args = json.loads(function_arguments)
        distance_m = args["time"]
        distance_unit = args["time_format"]
        move_spot_forward(robot=ROBOT, distance_m=distance_m, distance_unit=distance_unit, event=event)
    # ADD CASE FOR MOVING SPOT BACKWARD
    # elif(function_name == "move_spot_backward"):

    # spot stand (if not already)
    elif(robot_state.body_state != robot_state_pb2.RobotState.BodyState.STANDING and function_name == "stand"):
        make_spot_stand(ROBOT)

    elif(function_name == "power_on"):
        power_on_spot(ROBOT)

    elif(function_name == "power_off"):
        power_off_spot(ROBOT)

'''
-> Perception -> Control -> Action -> Environment -> LOOP until goal or condition is met (in our case when we tell spot to stop listening)
'''
def main():
    # username = "admin"
    # password = "sh384s6nnk6q"

    # Initializing speech recognition engine
    engine = pyttsx3.init()
    engine.say("Hello, how are you? Welcome to the Spot-LLM Program!")
    engine.runAndWait()

    # Authenticating SPOT for access
    # authenticate_SPOT = ROBOT.authenticate(username, password)
    if not authenticate_SPOT(robot=ROBOT):
        print("Cannot authenticate SPOT")
        return
    
    threads = []
    event = Event()
    try:
        # Main program loop
        while True:
            gpt_function = ""

            # TEST
            engine.say("What do you want to do? ")
            engine.runAndWait()

            ask_gpt = input("What do you want to do? ").lower()
            if check_stop_or_quit(ask_gpt, threads, event):
                break
            else:
                gpt_completion = generate_function(ask_gpt)
                check_gpt_response(gpt_completion)
                gpt_function = gpt_completion.choices[0].message.tool_calls[0].function.name
                gpt_arguments = gpt_completion.choices[0].message.tool_calls[0].function.arguments
                if gpt_function in {"stop", "quit"}:
                    if check_stop_or_quit(gpt_function, threads, event):
                        break
                elif(threads and threads[0].is_alive()):
                    print("An ongoing task detected.")
                else:
                    thread = Thread(target=task, args=(event, gpt_function, gpt_arguments))
                    threads = [thread]
                    print("starting task %s" % gpt_function)
                    thread.start()
    except Exception as e:
        print("Unexcpected Error has occured. Reason: " + str(e))

if __name__ == "__main__":
    main()
