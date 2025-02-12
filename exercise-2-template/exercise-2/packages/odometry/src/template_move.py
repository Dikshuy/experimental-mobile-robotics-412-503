#!/usr/bin/env python3

# import required libraries

class MoveNode(DTROS):
    def __init__(self, node_name):
        super(MoveNode, self).__init__(node_name=node_name, node_type=NodeType.GENERIC)
        # add your code here

        # subscribe to the left and right wheel encoder topics
        # publish to the wheels command topic

        # LEDs

        # define other variables    
        pass
        
    def callback(self, **kwargs):
        # add your code here
        # can define one or two depending on how you want to implement      
        pass
        
    def compute_distance_traveled(self, **kwargs):
        # add your code here
        pass
    
    def drive_straight(self, **kwargs):
        # add your code here
        pass
    
    def rotate_clockwise(self, **kwargs):
        # add your code here
        pass

    def rotate_anticlockwise(self, **kwargs):
        # add your code here
        pass

    def use_leds(self, **kwargs):
        # add your code here
        pass

    # define other functions if needed
    
    def run(self):
        rospy.sleep(2)  # wait for the node to initialize

        # add your code here
        # call the functions you have defined above for executing the movements
        pass

if __name__ == '__main__':
    # define class MoveNode
    # call the function run of class MoveNode
    rospy.spin()