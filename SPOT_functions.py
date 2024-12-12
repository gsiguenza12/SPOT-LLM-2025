import bosdyn.client
import bosdyn.client.util
from bosdyn.client.robot_command import RobotCommandClient, RobotCommandBuilder, blocking_stand, blocking_sit
import os, time

def authenticate_SPOT(robot):
    """
    function to authenticate to a SPOT ROBOT.
    If authentication is successfull: 
        the function will attempt to turn off estop and take control of the lease
    An exception will be raised and the reason will be given to the console.
    @return: True if success, False otherwise
    """
    try:
        bosdyn.client.util.authenticate(robot) #authenticate using bosdyn generic function
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

def move_spot_forward(robot, distance_m, distance_unit, event):
    UNITS = {"seconds", "minutes"}
    try:
        distance_m = int(distance_m)
        if distance_unit not in UNITS:
            raise Exception("Invalid distance time unit")
        if distance_unit == "minutes":
            distance_m = distance_m * 60
        if distance_m > 30:
            raise Exception("Exceed distance limit")
        if not robot.is_powered_on():
            raise Exception("SPOT is off")
        command_client = robot.ensure_client(RobotCommandClient.default_service_name)
        blocking_stand(command_client, timeout_sec=10)

        # Build a velocity command in the robot's frame. Positive x is forward.
        vel_cmd = RobotCommandBuilder.synchro_velocity_command(v_x=0.5, v_y=0, 
                                                    v_rot=0)
        
        # Calculate the time needed to travel the desired distance at the given speed.
        travel_time_s = distance_m / 0.5
        
        # Issue the command to start moving
        command_client.robot_command(lease=None, command=vel_cmd,
                                    end_time_secs=time.time() + travel_time_s)
        
        # Wait for Spot to finish moving
        event.wait(travel_time_s)
        
        # After moving the desired distance, stop Spot by sending a zero velocity command
        stop_cmd = RobotCommandBuilder.stop_command()
        command_client.robot_command(lease=None, command=stop_cmd)
        # blocking_sit(command_client, timeout_sec=10)
    except Exception as e:
        print("Failed to move spot SPOT.\nReason:" + str(e))


# TEST
# make spot stand
def make_spot_stand(robot, event):
    try:
        # command the robot to stand
        command_client = robot.ensure_client(RobotCommandClient.default_service_name)
        blocking_stand(command_client, timeout_sec=10)
        # After SPOT stands up, end command
        stop_cmd = RobotCommandBuilder.stop_command()
        command_client.robot_command(lease=None, command=stop_cmd)
    except Exception as e:
        print("Failed to make spot stand SPOT.\nReason:" + str(e))

# TEST
# def move_spot_backward(robot, distance_m, distance_unit, event):
#     UNITS = {"seconds", "minutes"}
#     try:
#         distance_m = int(distance_m)
#         if distance_unit not in UNITS:
#             raise Exception("Invalid distance time unit")
#         if distance_unit == "minutes":
#             distance_m = distance_m * 60
#         if distance_m > 30:
#             raise Exception("Exceed distance limit")
#         if not robot.is_powered_on():
#             raise Exception("SPOT is off")
#         command_client = robot.ensure_client(RobotCommandClient.default_service_name)
#         blocking_stand(command_client, timeout_sec=10)
# 
#         # Build a velocity command in the robot's frame. Positive x is forward. change to move in opposite direction
#         vel_cmd = RobotCommandBuilder.synchro_velocity_command(v_x=0.5, v_y=0,
#                                                                v_rot=0)
# 
#         # Calculate the time needed to travel the desired distance at the given speed.
#         travel_time_s = distance_m / 0.5
# 
#         # Issue the command to start moving
#         command_client.robot_command(lease=None, command=vel_cmd,
#                                      end_time_secs=time.time() + travel_time_s)
# 
#         # Wait for Spot to finish moving
#         event.wait(travel_time_s)
# 
#         # After moving the desired distance, stop Spot by sending a zero velocity command
#         stop_cmd = RobotCommandBuilder.stop_command()
#         command_client.robot_command(lease=None, command=stop_cmd)
#         blocking_sit(command_client, timeout_sec=10)
#     except Exception as e:
#         print("Failed to move spot SPOT.\nReason:" + str(e))

def stop_spot(robot):
    try:
        print("Stopping spot from the current action")
        command_client = robot.ensure_client(RobotCommandClient.default_service_name)
        stop_cmd = RobotCommandBuilder.stop_command()
        command_client.robot_command(lease=None, command=stop_cmd)
    except Exception as e:
        print("Failed to stop spot. Reason: " + str(e))