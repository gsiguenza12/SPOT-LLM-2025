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
def move_spot_backward(robot, distance_m, distance_unit, event):
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
 
         # Build a velocity command in the robot's frame. Positive x is forward. change to move in opposite direction
         vel_cmd = RobotCommandBuilder.synchro_velocity_command(v_x=-0.5, v_y=0,
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
         blocking_sit(command_client, timeout_sec=10)
     except Exception as e:
         print("Failed to move spot SPOT.\nReason:" + str(e))

def move_spot_left(robot, distance_m, distance_unit, event):
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
 
         # Build a velocity command in the robot's frame. Positive x is forward. change to move in opposite direction
         vel_cmd = RobotCommandBuilder.synchro_velocity_command(v_x=0, v_y=0.5,
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
         blocking_sit(command_client, timeout_sec=10)
     except Exception as e:
         print("Failed to move spot SPOT.\nReason:" + str(e))

def move_spot_right(robot, distance_m, distance_unit, event):
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
 
         # Build a velocity command in the robot's frame. Positive x is forward. change to move in opposite direction
         vel_cmd = RobotCommandBuilder.synchro_velocity_command(v_x=0, v_y=-0.5,
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
         blocking_sit(command_client, timeout_sec=10)
     except Exception as e:
         print("Failed to move spot SPOT.\nReason:" + str(e))

def stop_spot(robot):
    try:
        print("Stopping spot from the current action")
        command_client = robot.ensure_client(RobotCommandClient.default_service_name)
        stop_cmd = RobotCommandBuilder.stop_command()
        command_client.robot_command(lease=None, command=stop_cmd)
    except Exception as e:
             print("Failed to stop spot. Reason: " + str(e))

def raise_arm(robot):
    try: 
        print("Raising arm up and down")
        command_client = robot.ensure_client(RobotCommandClient.default_service_name)
        unstow_command_id = command_client.robot_command(unstow)

        block_until_arm_arrives(command_client, unstow_command_id, 3.0)

        # Make the arm pose RobotCommand
        # Build a position to move the arm to (in meters, relative to and expressed in the gravity aligned body frame).
        x = 0.75
        y = 0
        z = 0.25
        hand_ewrt_flat_body = geometry_pb2.Vec3(x=x, y=y, z=z)

        # Rotation as a quaternion
        qw = 1
        qx = 0
        qy = 0
        qz = 0
        flat_body_Q_hand = geometry_pb2.Quaternion(w=qw, x=qx, y=qy, z=qz)

        flat_body_T_hand = geometry_pb2.SE3Pose(position=hand_ewrt_flat_body,
                                                rotation=flat_body_Q_hand)

        robot_state = robot_state_client.get_robot_state()
        odom_T_flat_body = get_a_tform_b(robot_state.kinematic_state.transforms_snapshot,
                                         ODOM_FRAME_NAME, GRAV_ALIGNED_BODY_FRAME_NAME)

        odom_T_hand = odom_T_flat_body * math_helpers.SE3Pose.from_proto(flat_body_T_hand)

        # duration in seconds
        seconds = 2

        arm_command = RobotCommandBuilder.arm_pose_command(
            odom_T_hand.x, odom_T_hand.y, odom_T_hand.z, odom_T_hand.rot.w, odom_T_hand.rot.x,
            odom_T_hand.rot.y, odom_T_hand.rot.z, ODOM_FRAME_NAME, seconds)

        cmd_id = command_client.robot_command(arm_command)

    except Exception as e:
        print('Failed to raise the arm successfully. Reason: ' + str(e))
