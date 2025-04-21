import bosdyn.client
import bosdyn.client.util
from bosdyn.client.robot_command import RobotCommandClient, RobotCommandBuilder, blocking_stand, blocking_sit
import os, time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def authenticate_SPOT(robot):
    """
    function to authenticate to a SPOT ROBOT.
    If authentication is successfull: 
        the function will attempt to turn off estop and take control of the lease
    An exception will be raised and the reason will be given to the console.
    @return: True if success, False otherwise
    """
    try:
        # Get credentials from environment variables
        username = os.getenv('SPOT_USERNAME')
        password = os.getenv('SPOT_PASSWORD')
        
        if not username or not password:
            raise ValueError("SPOT credentials not found in environment variables")
            
        # Authenticate directly using the credentials
        robot.authenticate(username, password)
        robot.time_sync.wait_for_sync()
        
        estop_client = robot.ensure_client('estop') 
        estop_endpoint = bosdyn.client.estop.EstopEndpoint(client=estop_client, name='spotgpt_estop', estop_timeout=25.0)   #power cutoff after 25 seconds
        estop_endpoint.force_simple_setup()
        estop_keep_alive = bosdyn.client.estop.EstopKeepAlive(estop_endpoint)
        print(estop_client.get_status())

        lease_client = robot.ensure_client('lease')
        lease = lease_client.acquire()
        lease_keep_alive = bosdyn.client.lease.LeaseKeepAlive(lease_client, return_at_exit="False")
        return True
    except Exception as e:
        print("Authentication initialization failed.\nReason: " + str(e))
        return False

def power_on_spot(robot):
    """
    function to power on spot
    """
    try:
        if robot.is_powered_on():
            print("Robot is already on")
        else:
            robot.power_on(timeout_sec=20)
    except Exception as e:
        print("Failed to powering on SPOT.\nReason:" + str(e))

def power_off_spot(robot):
    """
    function to power off spot
    """
    try:
        if not robot.is_powered_on():
            print("Robot is already off")
        else:
            command_client = robot.ensure_client(RobotCommandClient.default_service_name)
            stop_command = RobotCommandBuilder.stop_command()
            selfright_command = RobotCommandBuilder.selfright_command()
            safe_power_off_command = RobotCommandBuilder.safe_power_off_command()
            command_client.robot_command(stop_command)
            command_client.robot_command(selfright_command)
            command_client.robot_command(safe_power_off_command)
    except Exception as e:
        print("Failed to powering off SPOT.\nReason:" + str(e))

def move_spot(robot, v_x, v_y, v_rot, duration, event):
    """
    Move SPOT with specified velocities for a given duration
    Args:
        robot: The SPOT robot instance
        v_x: Forward/backward velocity (m/s). Positive for forward, negative for backward
        v_y: Left/right velocity (m/s). Positive for right, negative for left
        v_rot: Rotational velocity (rad/s). Positive for clockwise, negative for counterclockwise
        duration: Duration of movement in seconds
        event: Event object for controlling the movement
    """
    try:
        if not robot.is_powered_on():
            raise Exception("SPOT is off")
        
        if duration > 30:
            raise Exception("Duration exceeds 30 seconds limit")
            
        command_client = robot.ensure_client(RobotCommandClient.default_service_name)
        blocking_stand(command_client, timeout_sec=10)

        # Build velocity command with specified parameters
        vel_cmd = RobotCommandBuilder.synchro_velocity_command(v_x=v_x, v_y=v_y, v_rot=v_rot)
        
        # Issue the command to start moving
        command_client.robot_command(lease=None, command=vel_cmd,
                                    end_time_secs=time.time() + duration)
        
        # Wait for Spot to finish moving
        event.wait(duration)
        
        # Stop Spot by sending a zero velocity command
        stop_cmd = RobotCommandBuilder.stop_command()
        command_client.robot_command(lease=None, command=stop_cmd)
        
    except Exception as e:
        print("Failed to move SPOT. Reason:" + str(e))

def stop_spot(robot):
    try:
        print("Stopping spot from the current action")
        command_client = robot.ensure_client(RobotCommandClient.default_service_name)
        stop_cmd = RobotCommandBuilder.stop_command()
        command_client.robot_command(lease=None, command=stop_cmd)
    except Exception as e:
             print("Failed to stop spot. Reason: " + str(e))
