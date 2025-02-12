#!/usr/bin/env python3

# potentially useful for question - 3

# import required libraries

class LaneFollowingNode(DTROS):
    def __init__(self, node_name):
        super(LaneFollowingNode, self).__init__(node_name=node_name, node_type=NodeType.CONTROL)
        # add your code here
        
        # select controller type ('P', 'PD', or 'PID')
        
        # PID gains 
        
        # control variables
        
        # movement parameters
        
        # initialize brige and publishers/subscribers
        
        # publisher for motor commands

        # define other variables as needed
        
    def preprocess_image(self, **kwargs):
        # add your code here
        pass
        
    def calculate_error(self, **kwargs):
        # add your code here
        pass
        
    def p_control(self, **kwargs):
        # add your code here
        pass
        
    def pd_control(self, **kwargs):
        # add your code here
        pass
        
    def pid_control(self, **kwargs):
        # add your code here
        pass
        
    def publish_cmd(self, **kwargs):
        # add your code here
        pass
        
    def image_callback(self, **kwargs):
        # add your code here
        pass

    # add other functions as needed

if __name__ == '__main__':
    node = LaneFollowingNode(node_name='lane_following_node')
    rospy.spin()