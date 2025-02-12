#!/usr/bin/env python3

# potentially useful for question - 2.2

# import required libraries

class LaneControllerNode(DTROS):
    def __init__(self, node_name):
        super(LaneControllerNode, self).__init__(node_name=node_name, node_type=NodeType.CONTROL)
        # add your code here
        
        # controller type
        
        # PID gains 
        
        # control variables
        
        # movement parameters
        
        # distance tracking
        
        # initialize publisher/subscribers

    def calculate_p_control(self, **kwargs):
        # add your code here
        pass

    def calculate_pd_control(self, **kwargs):
        # add your code here
        pass

    def calculate_pid_control(self, **kwargs):
        # add your code here
        pass

    def get_control_output(self, **kwargs):
        # add your code here
        pass

    def publish_cmd(self, **kwargs):
        # add your code here
        pass

    def yellow_lane_callback(self, **kwargs):
        # add your code here
        pass

    # add other functions as needed

if __name__ == '__main__':
    node = LaneControllerNode(node_name='lane_controller_node')
    rospy.spin()