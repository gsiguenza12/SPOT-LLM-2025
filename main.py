from gpt_module import generate_function, command_mapping
from threading import Thread, Event
from bosdyn.client import create_standard_sdk
from bosdyn.client.lease import LeaseKeepAlive
from dotenv import load_dotenv
import os

# Add import for new functions here
from SPOT_functions import authenticate_SPOT, stop_spot, power_off_spot, power_on_spot, move_spot
import json
from spot_speech_capability import main as speech_main
from spot_speech_capability import text_to_speech

# import for text to speech, speech to text
from gtts import gTTS
import pyttsx3
import sys
import subprocess

# Load environment variables
load_dotenv()

# How to implement a function:
#    Step 1: add to command list in main.py
#    Step 2: add the call to the function in task function in main.py
#    Step 3: add to gpt_module.py as tool
#    Step 4: add to SPOT_functions.py as function(details of function here)

COMMAND_LIST = {
    "power_on", 
    "power_off", 
    "move_spot",
    "stop",
    "quit",
    "execute_example"
    }

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

# to test
# mytext = "Hello welcome to the spot llm program!"

# which language you want to convert
# language = 'en'

# Passing the text and language to the engine,
# here we have marked slow=False. Which tells
# the module that the converted audio should
# have a high speed
# myobj = gTTS(text=mytext, lang=language, slow=False)

# Saving the converted audio in a mp3 file named
# welcome
# myobj.save("welcome.mp3")

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

def install_requirements(example_path):
    """
    Install requirements for an example if requirements.txt exists
    """
    requirements_path = os.path.join(example_path, 'requirements.txt')
    if os.path.exists(requirements_path):
        print(f"Installing requirements from {requirements_path}")
        try:
            import subprocess
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', requirements_path])
            print("Requirements installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"Error installing requirements: {e}")
            return False
    return True

def task(event, function_name, function_arguments):
    print("Attempting to run the function " + function_name)
    if(function_name == "move_spot"):
        args = json.loads(function_arguments)
        v_x = args["v_x"]
        v_y = args["v_y"]
        v_rot = args["v_rot"]
        duration = args["duration"]
        move_spot(robot=ROBOT, v_x=v_x, v_y=v_y, v_rot=v_rot, duration=duration, event=event)
    elif(function_name == "execute_example"):
        args = json.loads(function_arguments)
        example_name = args["example_name"]
        parameters = args.get("parameters", {})
        
        # Get the example path from the command mapping
        if example_name in command_mapping:
            example_path = command_mapping[example_name]
            print(f"Executing example: {example_name} from {example_path}")
            
            # Install requirements first
            if not install_requirements(os.path.dirname(example_path)):
                print("Failed to install requirements, aborting example execution")
                return
            
            try:
                # Add the example directory to Python path
                example_dir = os.path.dirname(example_path)
                if example_dir not in sys.path:
                    sys.path.append(example_dir)
                
                # Import and run the example module
                module_name = os.path.splitext(os.path.basename(example_path))[0]
                example_module = __import__(module_name)
                
                # Ensure we have a lease before running the example
                lease_client = ROBOT.ensure_client('lease')
                try:
                    # First try to acquire the lease normally
                    lease = lease_client.acquire()
                except Exception as e:
                    if "ResourceAlreadyClaimedError" in str(e):
                        print("Lease already claimed, attempting to take lease...")
                        try:
                            lease = lease_client.take()
                        except Exception as take_error:
                            print(f"Failed to take lease: {take_error}")
                            print("Please ensure no other program is controlling the robot")
                            return
                    else:
                        print(f"Failed to acquire lease: {e}")
                        print("Please ensure no other program is controlling the robot")
                        return
                
                lease_keepalive = LeaseKeepAlive(lease_client)
                
                try:
                    # Call the main function with our robot instance
                    if hasattr(example_module, 'main'):
                        example_module.main(robot=ROBOT)
                    else:
                        print(f"Example {example_name} does not have a main function")
                finally:
                    # Clean up the lease
                    lease_keepalive.shutdown()
                    lease_client.return_lease(lease)
                
            except Exception as e:
                print(f"Error executing example {example_name}: {str(e)}")
        else:
            print(f"Example {example_name} not found")
    elif(function_name == "power_on"):
        power_on_spot(ROBOT)
    elif(function_name == "power_off"):
        power_off_spot(ROBOT)
    elif(function_name == "stop"):
        stop_spot(ROBOT)


'''
-> Perception -> Control -> Action -> Environment -> LOOP until goal or condition is met (in our case when we tell spot to stop listening)
'''
def main():
    # username = "admin"
    # password = "sh384s6nnk6q"
    print(command_mapping)
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
            # acquire lease if not acquired
            
      
            gpt_function = ""
            # TEST
            engine.say("What do you want to do? ")
            engine.runAndWait()

            ask_gpt = speech_main()
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