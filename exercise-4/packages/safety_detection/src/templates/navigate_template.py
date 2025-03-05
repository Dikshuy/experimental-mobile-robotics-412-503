#!/usr/bin/env python3

# potentially useful for question - 1.5

# import required libraries
import rospy
from duckietown.dtros import DTROS, NodeType

class NavigationControl(DTROS):
    def __init__(self, node_name):
        super(NavigationControl, self).__init__(node_name=node_name, node_type=NodeType.CONTROL)
        # add your code here
        
        # publisher for wheel commands
        # NOTE: you can directly publish to wheel chassis using the car_cmd_switch_node topic in this assignment (check documentation)
        # you can also use your exercise 2 code
        
        # robot params

        # define other variables as needed
        
    def publish_velocity(self, **kwargs):
        # add your code here
        pass
        
    def stop(self, **kwargs):
        # add your code here
        pass
        
    def move_straight(self, **kwargs):
        # add your code here
        pass
        
    def turn_right(self, **kwargs):
        # add your code here
        pass
        
    def turn_left(self, **kwargs):
        # add your code here
        pass

    # add other functions as needed

if __name__ == '__main__':
    node = NavigationControl(node_name='navigation_control_node')
    rospy.spin()