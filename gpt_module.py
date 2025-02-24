from openai import OpenAI
import os

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
    api_key="redacted",
)
# set the output location
current_directory = os.getcwd()
# file_path = os.path.join(current_directory, 'src', 'gpt_output', 'output.json')
file_path = os.path.join(current_directory, 'gpt_output', 'output.json')
tools = [
    {
        "type": "function",
        "function": {
            "name": "move_spot_forward",
            "description": "Command a SPOT robot to move forward",
            "parameters": {
                "type": "object",
                "properties": {
                    "time": {
                        "type": "integer",
                        "description": "The time it takes for the robot to move forward.",
                    },
                    "time_format": {
                        "type": "string",
                        "enum": ["seconds", "minutes"],
                        "description": "The unit of time for this command. Make sure that it is either seconds or minutes. "
                        "Do not accept any other time format as a valid format. Ensure the time does not exceed 30 seconds",
                    },
                },
                "required": ["time", "time_format"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "move_spot_backward",
            "description": "Command a SPOT robot to move backward",
            "parameters": {
                "type": "object",
                "properties": {
                    "time": {
                        "type": "integer",
                        "description": "The time it takes for the robot to move backward.",
                    },
                    "time_format": {
                        "type": "string",
                        "enum": ["seconds", "minutes"],
                        "description": "The unit of time for this command. Make sure that it is either seconds or minutes. "
                        "Do not accept any other time format as a valid format. Ensure the time does not exceed 30 seconds",
                    },
                },
                "required": ["time", "time_format"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "move_spot_left",
            "description": "Command a SPOT robot to move left",
            "parameters": {
                "type": "object",
                "properties": {
                    "time": {
                        "type": "integer",
                        "description": "The time it takes for the robot to move left.",
                    },
                    "time_format": {
                        "type": "string",
                        "enum": ["seconds", "minutes"],
                        "description": "The unit of time for this command. Make sure that it is either seconds or minutes. "
                        "Do not accept any other time format as a valid format. Ensure the time does not exceed 30 seconds",
                    },
                },
                "required": ["time", "time_format"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "move_spot_right",
            "description": "Command a SPOT robot to move right",
            "parameters": {
                "type": "object",
                "properties": {
                    "time": {
                        "type": "integer",
                        "description": "The time it takes for the robot to move right.",
                    },
                    "time_format": {
                        "type": "string",
                        "enum": ["seconds", "minutes"],
                        "description": "The unit of time for this command. Make sure that it is either seconds or minutes. "
                        "Do not accept any other time format as a valid format. Ensure the time does not exceed 30 seconds",
                    },
                },
                "required": ["time", "time_format"],
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