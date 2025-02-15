#!/usr/bin/env python3

import os
import math
import rospy
import rosbag
from duckietown.dtros import DTROS, NodeType
from duckietown_msgs.msg import WheelEncoderStamped, WheelsCmdStamped
from lights import LightController


class TrajectoryNode(DTROS):
    def __init__(self, node_name):
        super(TrajectoryNode, self).__init__(node_name=node_name, node_type=NodeType.GENERIC)
        
        # topics
        self._vehicle_name = os.environ['VEHICLE_NAME']
        self._left_encoder_topic = f"/{self._vehicle_name}/left_wheel_encoder_node/tick"
        self._right_encoder_topic = f"/{self._vehicle_name}/right_wheel_encoder_node/tick"
        self._wheels_topic = f"/{self._vehicle_name}/wheels_driver_node/wheels_cmd"
        
        # encoder params
        self._ticks_left = 0
        self._ticks_right = 0
        self._initial_ticks_left = 0
        self._initial_ticks_right = 0
        
        # robot geometry
        self._wheel_radius = 0.0318
        self._wheel_separation = 0.05
        self._ticks_per_rotation = 135

        # light controler node
        self.light_controler = LightController()
        
        # topics
        self.sub_left = rospy.Subscriber(self._left_encoder_topic, WheelEncoderStamped, self.callback_left)
        self.sub_right = rospy.Subscriber(self._right_encoder_topic, WheelEncoderStamped, self.callback_right)
        self._publisher = rospy.Publisher(self._wheels_topic, WheelsCmdStamped, queue_size=1)
        
    def callback_left(self, data):
        # Update left wheel encoder ticks
        self._ticks_left = data.data
        
    def callback_right(self, data):
        # Update right wheel encoder ticks
        self._ticks_right = data.data
        
    def compute_distance_traveled(self, initial_left, initial_right, current_left, current_right):
        # Compute the distance traveled by the robot
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
            # Publish wheel commands to drive straight
            message = WheelsCmdStamped(vel_left=0.5*direction, vel_right=0.5*direction)
            self._publisher.publish(message)

            # Compute the distance traveled
            traveled = self.compute_distance_traveled(
                self._initial_ticks_left, 
                self._initial_ticks_right, 
                self._ticks_left, 
                self._ticks_right
            )
            
            # Stop the robot if the desired distance is reached
            if abs(traveled) >= distance:
                stop_msg = WheelsCmdStamped(vel_left=0, vel_right=0)
                self._publisher.publish(stop_msg)
                break
            
            rate.sleep()
    
    def drive_arc(self, radius, arc_angle, direction=1):
        # Drive the robot in an arc
        self._initial_ticks_left = self._ticks_left
        self._initial_ticks_right = self._ticks_right

        arc_length = radius * arc_angle
        
        track_width = self._wheel_separation
        outer_wheel_speed = 0.5 * direction
        inner_wheel_speed = outer_wheel_speed * (radius - track_width/2) / (radius + track_width/2)
        
        rate = rospy.Rate(10)
        while not rospy.is_shutdown():
            # Publish wheel commands to drive in an arc
            message = WheelsCmdStamped(vel_left=inner_wheel_speed, vel_right=outer_wheel_speed)
            self._publisher.publish(message)

            # Compute the distance traveled by the left wheel
            left_distance = self.compute_distance_traveled(
                self._initial_ticks_left, 
                self._initial_ticks_right, 
                self._ticks_left, 
                self._ticks_right
            )

            # Stop the robot if the desired arc length is reached
            if abs(left_distance) >= arc_length:
                stop_msg = WheelsCmdStamped(vel_left=0, vel_right=0)
                self._publisher.publish(stop_msg)
                break
            
            rate.sleep()
    
    def draw_d_shape(self):
        # in this function, i implemented this arc function to draw a D shape trajectory
        # in case of a perfect D shape, however in your assignment you were supposed to 
        # implement a function to draw a somewhat D shape trajectory, nonetheless, i will
        # implement the perfect D shape trajectory here just to show how to draw a perfect arc

        # Draw a D shape trajectory
        rospy.loginfo("vertical line")
        self.drive_straight(1.0, direction=1)
        rospy.sleep(1)
        
        rospy.loginfo("arc")
        self.drive_arc(radius=0.5, arc_angle=math.pi, direction=1)
        rospy.sleep(1)

    def run(self):
        # Run the trajectory node
        try:
            self.light_controler.set_led_color([1, 0, 0])
            rospy.sleep(2)
            self.light_controler.set_led_color([[1, 1, 0, 1],[1, 0, 0, 1],[1, 0, 0, 1],[1, 0, 0, 1],[1, 1, 0, 1]])
            self.draw_d_shape()
            self.light_controler.set_led_color([1, 0, 0])
            rospy.sleep(2)
        finally:
            self._bag.close()
            self.light_controler.set_led_color([0, 0, 0])

if __name__ == '__main__':
    # Initialize and run the node
    node = TrajectoryNode(node_name='trajectory_tracking_node')
    node.run()
    rospy.spin()