#!/usr/bin/env python3

# import required libraries

class CameraReaderNode(DTROS):
    def __init__(self, node_name):
        super(CameraReaderNode, self).__init__(node_name=node_name, node_type=NodeType.VISUALIZATION)

        # add your code here

        # subscribe to the camera topic
        # publish to the annotated image topic

        pass

    def callback(self, **kwargs):
        # add your code here

        # convert JPEG bytes to CV image
        # convert to grayscale
        # annotate the image
        # publish annotated grayscale image

        pass

    # define other functions if needed

if __name__ == '__main__':
    # define class CameraReaderNode
    # call the function run of class CameraReaderNode
    rospy.spin()