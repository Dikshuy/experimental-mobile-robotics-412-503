#!/usr/bin/env python3

# potentially useful for question - 1.6

# import required libraries

class BehaviorController(DTROS):
    def __init__(self, node_name):
        super(BehaviorController, self).__init__(node_name=node_name, node_type=NodeType.CONTROL)
        # add your code here
        
        # call navigation control node
        
        # define parameters
        
        # Color ranges in HSV

        # LED stuff
        
        # subscribe to camera feed
        
        # define other variables as needed
        
    def set_led_pattern(self, **kwargs):
        # add your code here
        pass
        
    def detect_line(self, **kwargs):
        # add your code here
        pass
    
    def execute_blue_line_behavior(self, **kwargs):
        # add your code here
        pass
        
    def execute_red_line_behavior(self, **kwargs):
        # add your code here
        pass
        
    def execute_yellow_line_behavior(self, **kwargs):
        # add your code here
        pass
        
    def callback(self, **kwargs):
        # add your code here
        pass

    # add other functions as needed

if __name__ == '__main__':
    node = BehaviorController(node_name='behavior_controller_node')
    rospy.spin()