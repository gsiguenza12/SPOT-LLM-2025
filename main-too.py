from gpt_module import generate_function
from threading import Thread, Event
from bosdyn.client import create_standard_sdk
from SPOT_functions import authenticate_SPOT, stop_spot, power_off_spot, power_on_spot, move_spot_forward
import json
import pyttsx3

# Define SPOT ROBOT
class SpotRobot:

    # Initialize SPOT to connect and run functions
    def __init__(self, ip_address):
        self.sdk = create_standard_sdk('SpotClient')
        self.robot = self.sdk.create_robot(ip_address)
        self.threads = []
        self.event = Event()
        self.tts_engine = pyttsx3.init()
        
        if not authenticate_SPOT(robot=self.robot):
            print("Cannot authenticate SPOT")
            exit(1)

    # SPOT Speak Function
    def speak(self, text):
        """Handles text-to-speech output."""
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

    # SPOT Multi-thread Handling
    def clean_tasks(self):
        """Stops and cleans up running tasks."""
        if self.threads and self.threads[0].is_alive():
            self.event.set()
            self.threads[0].join()
            self.event.clear()
    
    # SPOT Run Command Helper Functions
    def execute_task(self, function_name, function_arguments):
        """Executes a given robot task in a separate thread."""
        if function_name in COMMAND_HANDLERS:
            self.clean_tasks()
            thread = Thread(target=COMMAND_HANDLERS[function_name], args=(self.robot, function_arguments, self.event))
            self.threads = [thread]
            thread.start()
        else:
            print(f"Unknown command: {function_name}")

    # GPT Processing User Input and Run Command
    def process_gpt_command(self, user_input):
        """Processes user input by querying GPT and executing the returned command."""
        try:
            gpt_completion = generate_function(user_input)
            function_name, function_arguments = parse_gpt_response(gpt_completion)
            self.execute_task(function_name, function_arguments)
        except ValueError as e:
            print(f"GPT Error: {e}")
    
    # SPOT STOP Function
    def check_stop_or_quit(self, command):
        """Handles stop and quit commands."""
        if command in {"stop", "quit"}:
            self.clean_tasks()
            stop_spot(self.robot)
            if command == "quit":
                print("Quitting program")
                exit(0)
            return True
        return False

# Command Handlers
def move_spot_forward_handler(robot, arguments, event):
    args = json.loads(arguments)
    move_spot_forward(robot=robot, distance_m=args["time"], distance_unit=args["time_format"], event=event)

def power_on_spot_handler(robot):
    power_on_spot(robot)

def power_off_spot_handler(robot):
    power_off_spot(robot)

# List of Command Handlers
COMMAND_HANDLERS = {
    "move_spot_forward": move_spot_forward_handler,
    "power_on": power_on_spot_handler,
    "power_off": power_off_spot_handler,
}

def parse_gpt_response(response):
    """Parses and validates GPT response."""
    try:
        choices = response.choices[0]
        if choices.finish_reason != "tool_calls":
            raise ValueError("GPT did not respond with a valid function")
        tool_call = choices.message.tool_calls[0]
        return tool_call.function.name, tool_call.function.arguments
    except Exception as e:
        raise ValueError(f"Invalid GPT response: {e}")

def main():
    robot_controller = SpotRobot("192.168.80.3")
    robot_controller.speak("Hello, welcome to the Spot-LLM Program!")
    
    while True:
        user_input = input("What do you want to do? ").lower()
        if robot_controller.check_stop_or_quit(user_input):
            break
        robot_controller.process_gpt_command(user_input)

if __name__ == "__main__":
    main()
