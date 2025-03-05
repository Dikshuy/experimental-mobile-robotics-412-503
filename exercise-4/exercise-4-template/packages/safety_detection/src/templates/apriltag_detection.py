#!/usr/bin/env python3

# potentially useful for part 1 of exercise 4

# import required libraries
import rospy
from duckietown.dtros import DTROS, NodeType

class ApriltagNode(DTROS):

    def __init__(self, node_name):
        super(ApriltagNode, self).__init__(node_name=node_name, node_type=NodeType.CONTROL)

        # add your code here

        # call navigation control node

        # initialize dt_apriltag detector

        # subscribe to camera feed

        # define other variables as needed

    def sign_to_led(self, **kwargs):
        pass

    def process_image(self, **kwargs):
        pass

    def publish_augmented_img(self, **kwargs):
        pass

    def publish_leds(self, **kwargs):
        pass

    def detect_tag(self, **kwargs):
        pass

    def camera_callback(self, **kwargs):
        pass


if __name__ == '__main__':
    # create the node
    node = ApriltagNode(node_name='apriltag_detector_node')
    rospy.spin()
    
