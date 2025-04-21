from gpt_module import generate_function
from threading import Thread, Event
from bosdyn.client import create_standard_sdk
from SPOT_functions import authenticate_SPOT, stop_spot
from command_handlers import COMMAND_HANDLERS
import pyttsx3
from websocket import create_connection
import traceback

# Define SPOT Robot Class
class SpotRobot:
    def __init__(self, ip_address, ws_url=None):
        """Initialize SPOT robot, WebSocket connection (if provided), and dependencies."""
        self.sdk = create_standard_sdk('SpotClient')
        self.robot = self.sdk.create_robot(ip_address)
        self.threads = []
        self.event = Event()
        self.tts_engine = pyttsx3.init()
        self.ws = create_connection(ws_url) if ws_url else None

        if not authenticate_SPOT(robot=self.robot):
            print("Cannot authenticate SPOT")
            exit(1)

    def speak(self, text):
        """Handles text-to-speech output."""
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

    def send_ws_message(self, message):
        """Send message over WebSocket if connected."""
        if self.ws:
            try:
                self.ws.send(message)
            except Exception as e:
                print(f"WebSocket Error: {e}")

    def clean_tasks(self):
        """Stops and cleans up running tasks."""
        if self.threads and self.threads[0].is_alive():
            self.event.set()
            self.threads[0].join()
            self.event.clear()

    def execute_task(self, function_name, function_arguments):
        """Executes a given robot task in a separate thread."""
        if function_name in COMMAND_HANDLERS:
            self.clean_tasks()
            thread = Thread(target=COMMAND_HANDLERS[function_name], args=(self.robot, function_arguments, self.event))
            self.threads = [thread]
            thread.start()
            self.send_ws_message(f"Executing command: {function_name}")
        else:
            print(f"Unknown command: {function_name}")
            self.send_ws_message(f"Error: Unknown command {function_name}")

    def process_gpt_command(self, user_input):
        """Processes user input, queries GPT, and executes the returned command."""
        try:
            gpt_completion = generate_function(user_input)
            function_name, function_arguments = parse_gpt_response(gpt_completion)
            self.execute_task(function_name, function_arguments)
        except ValueError as e:
            print(f"GPT Error: {e}")
            self.send_ws_message(f"GPT Error: {e}")

    def check_stop_or_quit(self, command):
        """Handles stop and quit commands."""
        if command in {"stop", "quit"}:
            self.clean_tasks()
            stop_spot(self.robot)
            if command == "quit":
                print("Quitting program")
                self.send_ws_message("Quitting program")
                exit(0)
            return True
        return False


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
    """Main function to start the SpotRobot and handle commands."""
    robot_controller = SpotRobot(ip_address="192.168.80.3", ws_url="ws://localhost:8001/")
    # robot_controller.speak("Hello, welcome to the Spot-LLM Program!")
    from spot_controller import SpotController
    with SpotController(username=SPOT_USERNAME, password=SPOT_PASSWORD, robot_ip=ROBOT_IP) as spot:
        globals()["spot_global"] = spot
        
    while True:
        try:
            user_input = input("What do you want to do? ").lower()
            if robot_controller.check_stop_or_quit(user_input):
                break
            robot_controller.process_gpt_command(user_input)
        except Exception as e:
            print(f"Unexpected Error: {traceback.format_exc()}")
            robot_controller.send_ws_message(f"Unexpected Error: {e}")


if __name__ == "__main__":
    main()