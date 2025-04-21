import bosdyn.client
import bosdyn.client.util
from bosdyn.client.robot_command import RobotCommandClient, RobotCommandBuilder, blocking_stand
import bosdyn.client.estop
import bosdyn.client.lease
import time

def authenticate_spot(robot):
    """Authenticate and initialize Spot robot."""
    try:
        bosdyn.client.util.authenticate(robot)
        robot.time_sync.wait_for_sync()
        
        estop_client = robot.ensure_client(bosdyn.client.estop.EstopClient.default_service_name)
        estop_endpoint = bosdyn.client.estop.EstopEndpoint(client=estop_client, name='spot_estop', estop_timeout=25.0)
        estop_endpoint.force_simple_setup()
        estop_keep_alive = bosdyn.client.estop.EstopKeepAlive(estop_endpoint)
        
        lease_client = robot.ensure_client(bosdyn.client.lease.LeaseClient.default_service_name)
        lease = lease_client.acquire()
        lease_keep_alive = bosdyn.client.lease.LeaseKeepAlive(lease_client, return_at_exit=False)
        
        return True
    except Exception as e:
        print(f"Authentication failed: {e}")
        return False 

def power_on_spot(robot):
    """Power on Spot robot."""
    try:
        if robot.is_powered_on():
            print("Robot is already powered on.")
        else:
            robot.power_on(timeout_sec=20)
    except Exception as e:
        print(f"Failed to power on Spot: {e}")

def power_off_spot(robot):
    """Power off Spot robot."""
    try:
        if not robot.is_powered_on():
            print("Robot is already powered off.")
        else:
            command_client = robot.ensure_client(RobotCommandClient.default_service_name)
            command_client.robot_command(RobotCommandBuilder.safe_power_off_command())
    except Exception as e:
        print(f"Failed to power off Spot: {e}")

def move_spot(robot, direction, distance, unit, event):
    """Move Spot in a specified direction."""
    DIRECTIONS = {
        "forward": (0.5, 0, 0),
        "backward": (-0.5, 0, 0),
        "left": (0, 0.5, 0),
        "right": (0, -0.5, 0)
    }
    UNITS = {"seconds", "minutes"}
    
    try:
        if unit not in UNITS:
            raise ValueError("Invalid time unit.")
        if unit == "minutes":
            distance *= 60
        if distance > 30:
            raise ValueError("Distance limit exceeded.")
        if not robot.is_powered_on():
            raise RuntimeError("Spot is powered off.")

        command_client = robot.ensure_client(RobotCommandClient.default_service_name)
        blocking_stand(command_client, timeout_sec=10)
        
        v_x, v_y, v_rot = DIRECTIONS.get(direction, (0, 0, 0))
        vel_cmd = RobotCommandBuilder.synchro_velocity_command(v_x=v_x, v_y=v_y, v_rot=v_rot)
        command_client.robot_command(vel_cmd, end_time_secs=time.time() + distance / 0.5)
        
        event.wait(distance)
        stop_spot(robot)
    except Exception as e:
        print(f"Failed to move Spot {direction}: {e}")

def stop_spot(robot):
    """Stop Spot immediately."""
    try:
        command_client = robot.ensure_client(RobotCommandClient.default_service_name)
        command_client.robot_command(RobotCommandBuilder.stop_command())
    except Exception as e:
        print(f"Failed to stop Spot: {e}")