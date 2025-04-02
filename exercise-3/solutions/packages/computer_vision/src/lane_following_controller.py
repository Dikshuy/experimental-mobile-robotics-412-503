#!/usr/bin/env python3

import os
import rospy
import numpy as np
from duckietown.dtros import DTROS, NodeType
from std_msgs.msg import Float32MultiArray
from duckietown_msgs.msg import Twist2DStamped

class LaneControllerNode(DTROS):
    def __init__(self, node_name):
        super(LaneControllerNode, self).__init__(node_name=node_name, node_type=NodeType.CONTROL)
        
        self._vehicle_name = os.environ['VEHICLE_NAME']
        
        # Controller parameters
        self.controller_type = rospy.get_param("~controller_type", "pid")
        
        # PID gains (random params)
        self.Kp = rospy.get_param("~Kp", 0.05)
        self.Ki = rospy.get_param("~Ki", 0.005)
        self.Kd = rospy.get_param("~Kd", 0.0005)
        
        # Control variables
        self.last_error = 0
        self.integral = 0
        self.last_time = rospy.get_time()
        
        # Movement parameters
        self.linear_velocity = 0.3
        self.max_angular_velocity = 8.0
        
        # Distance tracking
        self.start_time = rospy.get_time()
        self.distance_traveled = 0
        self.target_distance = 1.5
        
        # Velocity publisher
        self.vel_pub = rospy.Publisher(f'/{self._vehicle_name}/car_cmd_switch_node/cmd', Twist2DStamped, queue_size=1)
        
        # Lane subscribers
        self.yellow_sub = rospy.Subscriber('~/yellow_lane', Float32MultiArray, self.yellow_lane_callback, queue_size=1)
        self.white_sub = rospy.Subscriber('~/white_lane', Float32MultiArray, self.white_lane_callback, queue_size=1)

    def calculate_p_control(self, error):
        return self.Kp * error

    def calculate_pd_control(self, error):
        current_time = rospy.get_time()
        dt = current_time - self.last_time
        
        if dt <= 0:
            return self.calculate_p_control(error)
        
        derivative = (error - self.last_error) / dt
        self.last_error = error
        self.last_time = current_time
        
        return self.Kp * error + self.Kd * derivative

    def calculate_pid_control(self, error):
        current_time = rospy.get_time()
        dt = current_time - self.last_time
        
        if dt <= 0:
            return self.calculate_pd_control(error)
        
        self.integral += error * dt
        derivative = (error - self.last_error) / dt
        
        self.last_error = error
        self.last_time = current_time
        
        return self.Kp * error + self.Ki * self.integral + self.Kd * derivative

    def get_control_output(self, error):
        if self.controller_type == "p":
            return self.calculate_p_control(error)
        elif self.controller_type == "pd":
            return self.calculate_pd_control(error)
        else:  # pid
            return self.calculate_pid_control(error)

    def publish_command(self, v, omega):
        msg = Twist2DStamped()
        msg.v = v
        msg.omega = np.clip(omega, -self.max_angular_velocity, self.max_angular_velocity)
        self.vel_pub.publish(msg)
        
        # Update distance traveled
        current_time = rospy.get_time()
        dt = current_time - self.last_time
        self.distance_traveled += v * dt
        
        # Stop if target distance reached
        if self.distance_traveled >= self.target_distance:
            self.publish_command(0, 0)
            rospy.signal_shutdown("Target distance reached")

    def yellow_lane_callback(self, msg):
        if len(msg.data) != 2:
            return
            
        lane_x = msg.data[0]
        image_center = 320  # 640x480 image - cross check this
        
        # Calculate error (positive error means lane is to the left)
        error = (lane_x - image_center) / image_center
        
        # Get control output
        omega = self.get_control_output(error)
        
        # Publish command
        self.publish_command(self.linear_velocity, omega)

    def white_lane_callback(self, msg):
        pass

if __name__ == '__main__':
    node = LaneControllerNode(node_name='lane_controller_node')
    rospy.spin()