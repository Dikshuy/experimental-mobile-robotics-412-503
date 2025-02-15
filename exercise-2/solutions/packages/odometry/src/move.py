#!/usr/bin/env python3

import os
import math
import rospy
from duckietown.dtros import DTROS, NodeType
from duckietown_msgs.msg import WheelEncoderStamped, WheelsCmdStamped


class MoveNode(DTROS):
    def __init__(self, node_name):
        # Initialize the DTROS parent class
        super(MoveNode, self).__init__(node_name=node_name, node_type=NodeType.GENERIC)
        
        # Get the vehicle name from the environment variables
        self._vehicle_name = os.environ['VEHICLE_NAME']
        
        # Define the topics for the wheel encoders and wheel commands
        self._left_encoder_topic = f"/{self._vehicle_name}/left_wheel_encoder_node/tick"
        self._right_encoder_topic = f"/{self._vehicle_name}/right_wheel_encoder_node/tick"
        self._wheels_topic = f"/{self._vehicle_name}/wheels_driver_node/wheels_cmd"
        
        # Initialize encoder tick counts
        self._ticks_left = 0
        self._ticks_right = 0
        self._initial_ticks_left = 0
        self._initial_ticks_right = 0
        
        # Robot geometry parameters
        self._wheel_radius = 0.0318
        self._wheel_separation = 0.05
        self._ticks_per_rotation = 135

        # Speed of the wheels
        self.veh_speed = 0.5
        
        # Subscribers for the wheel encoders
        self.sub_left = rospy.Subscriber(self._left_encoder_topic, WheelEncoderStamped, self.callback_left)
        self.sub_right = rospy.Subscriber(self._right_encoder_topic, WheelEncoderStamped, self.callback_right)
        
        # Publisher for the wheel commands
        self._publisher = rospy.Publisher(self._wheels_topic, WheelsCmdStamped, queue_size=1)
        
    def callback_left(self, data):
        # Callback function for the left wheel encoder
        self._ticks_left = data.data
        
    def callback_right(self, data):
        # Callback function for the right wheel encoder
        self._ticks_right = data.data
        
    def compute_distance_traveled(self, initial_left, initial_right, current_left, current_right):
        # Compute the distance traveled by the robot based on encoder ticks
        delta_left = current_left - initial_left
        delta_right = current_right - initial_right

        distance_left = (delta_left / self._ticks_per_rotation) * (2 * math.pi * self._wheel_radius)
        distance_right = (delta_right / self._ticks_per_rotation) * (2 * math.pi * self._wheel_radius)
        
        return (distance_left + distance_right) / 2
    
    def drive_straight(self, distance, direction=1):
        # Drive the robot straight for a given distance
        self._initial_ticks_left = self._ticks_left
        self._initial_ticks_right = self._ticks_right
        
        rate = rospy.Rate(10)
        while not rospy.is_shutdown():
            # Publish the wheel commands to drive straight
            message = WheelsCmdStamped(vel_left=self.veh_speed*direction, vel_right=self.veh_speed*direction)
            self._publisher.publish(message)

            # Compute the distance traveled
            distance_traveled = self.compute_distance_traveled(
                self._initial_ticks_left, 
                self._initial_ticks_right, 
                self._ticks_left, 
                self._ticks_right
            )
            
            # Stop the robot if the desired distance is reached
            if abs(distance_traveled) >= distance:
                stop_msg = WheelsCmdStamped(vel_left=0, vel_right=0)
                self._publisher.publish(stop_msg)
                break
            
            rate.sleep()
    
    def rotate_anticlockwise(self, angle):
        # Rotate the robot anticlockwise by a given angle
        self._initial_ticks_left = self._ticks_left
        self._initial_ticks_right = self._ticks_right
        
        rate = rospy.Rate(20)
        while not rospy.is_shutdown():
            # Publish the wheel commands to rotate anticlockwise
            message = WheelsCmdStamped(vel_left=0.0, vel_right=self.veh_speed)
            self._publisher.publish(message)
            
            # Compute the rotation angle
            delta_left = self._ticks_left - self._initial_ticks_left
            delta_right = self._ticks_right - self._initial_ticks_right
            
            rotation = (delta_right - delta_left) * (2 * self._wheel_radius / self._wheel_separation)
            
            # Stop the robot if the desired angle is reached
            if abs(rotation) >= abs(angle):
                stop_msg = WheelsCmdStamped(vel_left=0, vel_right=0)
                self._publisher.publish(stop_msg)
                break
            
            rate.sleep()

    def rotate_clockwise(self, angle):
        # Rotate the robot clockwise by a given angle
        self._initial_ticks_left = self._ticks_left
        self._initial_ticks_right = self._ticks_right
        
        rate = rospy.Rate(20)
        while not rospy.is_shutdown():
            # Publish the wheel commands to rotate clockwise
            message = WheelsCmdStamped(vel_left=self.veh_speed, vel_right=0.0)
            self._publisher.publish(message)
            
            # Compute the rotation angle
            delta_left = self._ticks_left - self._initial_ticks_left
            delta_right = self._ticks_right - self._initial_ticks_right
            
            rotation = (delta_right - delta_left) * (2 * self._wheel_radius / self._wheel_separation)
            
            # Stop the robot if the desired angle is reached
            if abs(rotation) >= abs(angle):
                stop_msg = WheelsCmdStamped(vel_left=0, vel_right=0)
                self._publisher.publish(stop_msg)
                break
            
            rate.sleep()
    
    def run(self):
        # Wait for the subscribers to connect
        rospy.sleep(2)
        
        # Drive straight forward and backward
        rospy.loginfo("Driving forward 1.25 meters")
        self.drive_straight(1.25, direction=1)
        rospy.sleep(1)
        
        rospy.loginfo("Driving backward 1.25 meters")
        self.drive_straight(1.25, direction=-1)
        rospy.sleep(1)
        
        # Rotate 90 degrees clockwise
        rospy.loginfo("Rotating 90 degrees clockwise")
        self.rotate_clockwise(90)

        # Rotate 90 degrees counterclockwise
        rospy.loginfo("Rotating 90 degrees counterclockwise")
        self.rotate_anticlockwise(90)

if __name__ == '__main__':
    # Initialize the node and run it
    node = MoveNode(node_name='robot_movement_node')
    node.run()
    rospy.spin()