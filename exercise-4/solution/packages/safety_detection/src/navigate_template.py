#!/usr/bin/env python3

"""
    TESTED ->  needs tuning
"""

import os
import rospy
import math
import time
from duckietown.dtros import DTROS, NodeType
from duckietown_msgs.msg import Twist2DStamped

class NavigationControl():
    def __init__(self):
        self._vehicle_name = os.environ['VEHICLE_NAME']

        # Publisher for wheel commands
        self.vel_pub = rospy.Publisher(
            f'/{self._vehicle_name}/car_cmd_switch_node/cmd',
            Twist2DStamped,
            queue_size=1
        )
        
        # Robot parameters
        self.wheel_base = 0.05          # Distance between wheels in meters
        self.wheel_radius = 0.0318      # Wheel radius in meters
        
    def publish_velocity(self, v, omega):
        msg = Twist2DStamped()
        msg.v = v
        msg.omega = omega
        self.vel_pub.publish(msg)
        
    def stop(self, duration):
        self.publish_velocity(0, 0)
        rospy.sleep(duration)
        
    def move_straight(self, distance, speed=0.3):
        duration = abs(distance / speed)
        start_time = rospy.get_time()
        
        while (rospy.get_time() - start_time) < duration:
            self.publish_velocity(speed, 0)
            rospy.sleep(0.1)
            
        self.stop(0.5)
        
    def turn_right(self, speed=0.3, omega=-2.0):
        duration = (math.pi/2) / abs(omega)
        start_time = rospy.get_time()
        
        while (rospy.get_time() - start_time) < duration:
            self.publish_velocity(speed, omega)
            rospy.sleep(0.1)
            
        self.stop(0.5)
        
    def turn_left(self, speed=0.3, omega=2.0):
        duration = (math.pi/2) / abs(omega)
        start_time = rospy.get_time()
        
        while (rospy.get_time() - start_time) < duration:
            self.publish_velocity(speed, omega)
            rospy.sleep(0.1)
            
        self.stop(0.5)

class NavigationControlNode(DTROS):
    def __init__(self, node_name):
        super(NavigationControl, self).__init__(node_name=node_name, node_type=NodeType.CONTROL)

        self.navigation_controller = NavigationControl()


if __name__ == '__main__':
    node = NavigationControl(node_name='navigation_control_node')
    rospy.spin()