#!/usr/bin/env python3

# potentially useful for part 2 of exercise 4

# import required libraries
import rospy
from duckietown.dtros import DTROS, NodeType

class SafeNavigationNode(DTROS):

    def __init__(self, node_name):
        super(SafeNavigationNode, self).__init__(node_name=node_name, node_type=NodeType.LOCALIZATION)

        # add your code here

        # call navigation control node

        # subscribe to camera feed

        # define other variables as needed

    def detect_bot(self, **kwargs):
        pass

    def manuver_around_bot(self, **kwargs):
        pass

    def image_callback(self, **kwargs):
        pass

if __name__ == '__main__':
    # create the node
    node = SafeNavigationNode(node_name='april_tag_detector')
    rospy.spin()
