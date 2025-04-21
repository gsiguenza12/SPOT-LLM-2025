from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
"""
The provided code defines a list of tools, each represented as a dictionary. 
These tools are functions designed to control a SPOT robot, a type of robotic system. 
Each dictionary within the list specifies the type of tool (in this case, all are functions) 
and details about the function itself, including its name, description, and any parameters it requires. 
This provides a structured way to define and document the functions available for controlling a SPOT robot, 
ensuring that each function is clearly described and that any required parameters are well-defined.
"""


client = OpenAI(
    # This is the default and can be omitted
    api_key=os.getenv('OPENAI_API_KEY'),
)
# set the output location
current_directory = os.getcwd()
# file_path = os.path.join(current_directory, 'src', 'gpt_output', 'output.json')
file_path = os.path.join(current_directory, 'gpt_output', 'output.json')
tools = [
    {
        "type": "function",
        "function": {
            "name": "move_spot",
            "description": "Command a SPOT robot to move with specified velocities. Use these predefined patterns:\n" +
                         "- Forward: v_x = 0.5, v_y = 0, v_rot = 0\n" +
                         "- Backward: v_x = -0.5, v_y = 0, v_rot = 0\n" +
                         "- Left: v_x = 0, v_y = 0.5, v_rot = 0\n" +
                         "- Right: v_x = 0, v_y = -0.5, v_rot = 0\n" +
                         "- Rotate clockwise: v_x = 0, v_y = 0, v_rot = 0.5\n" +
                         "- Rotate counterclockwise: v_x = 0, v_y = 0, v_rot = -0.5\n" +
                         "For all movements, use a default duration of 2 seconds unless specified otherwise.",
            "parameters": {
                "type": "object",
                "properties": {
                    "v_x": {
                        "type": "number",
                        "description": "Forward/backward velocity (m/s). Positive for forward, negative for backward. Use predefined values: 0.5 for forward, -0.5 for backward, 0 for sideways/rotation",
                    },
                    "v_y": {
                        "type": "number",
                        "description": "Left/right velocity (m/s). Positive for right, negative for left. Use predefined values: 0.5 for left, -0.5 for right, 0 for forward/backward/rotation",
                    },
                    "v_rot": {
                        "type": "number",
                        "description": "Rotational velocity (rad/s). Positive for clockwise, negative for counterclockwise. Use predefined values: 0.5 for clockwise, -0.5 for counterclockwise, 0 for linear movement",
                    },
                    "duration": {
                        "type": "number",
                        "description": "Duration of movement in seconds. Default to 2 seconds unless specified otherwise",
                    }
                },
                "required": ["v_x", "v_y", "v_rot", "duration"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "power_on",
            "description": "Command a SPOT robot to power on",
        }
    },
    {
        "type": "function",
        "function": {
            "name": "power_off",
            "description": "Command a SPOT robot to power off",
        }
    },
    {
        "type": "function",
        "function": {
            "name": "stop",
            "description": "Command SPOT robot to stop the current action",
        }
    },
    {
        "type": "function",
        "function": {
            "name": "quit",
            "description": "Stop SPOT from the current action and quit the program"
        }
    }
]

def generate_function(user_input):
    """
    Generates a response using the GPT-3.5-turbo model based on the provided user input.
    Args:
        user_input (str): The input prompt from the user.
    Returns:
        completion: The completion object containing the generated response.
    The function performs the following steps:
    1. Initializes a list of messages with a system message and the user input.
    2. Calls the GPT-3.5-turbo model to generate a response.
    3. Continuously updates the conversation with the assistant's messages and user inputs until the response is complete.
    4. Writes the final response to an output file in JSON format.
    5. Ensures the directory for the output file exists, creating it if necessary.
    """
    '''
    Call gpt using the current settings
    if user_input prompt is valid:
      gpt will create a response of the current function_name with arguments parameter based of actions
      completion.choices[0] need to be == tool_calls to generate this valid response
    '''
    messages = []
    messages.append({"role": "system", "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."})
    messages.append({"role": "user", "content": user_input})
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools
    )
    while completion.choices[0].finish_reason == "stop":
        assistant_message = completion.choices[0].message
        messages.append(assistant_message)
        print(assistant_message.content)
        user_input = input("")
        messages.append({"role": "user", "content": user_input})
        
        completion = client.chat.completions.create(
          model="gpt-4o-mini",
          messages=messages,
          tools=tools
        )
        
    # with open(file_path, "w") as outfile:  # Write the response to output.json
    #     outfile.write(completion.model_dump_json())
    # return completion
    # Ensure the directory exists
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(file_path, "w") as outfile:  # Write the response to output.json
        outfile.write(completion.model_dump_json())
    return completion