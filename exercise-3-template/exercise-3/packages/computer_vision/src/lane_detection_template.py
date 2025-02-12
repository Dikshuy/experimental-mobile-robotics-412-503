#!/usr/bin/env python3

# potentially useful for question - 1.1 - 1.4 and 2.1

# import required libraries

class LaneDetectionNode(DTROS):
    def __init__(self, node_name):
        super(LaneDetectionNode, self).__init__(node_name=node_name, node_type=NodeType.PERCEPTION)
        # add your code here
        
        # camera calibration parameters (intrinsic matrix and distortion coefficients)
        
        # color detection parameters in HSV format
        
        # initialize bridge and subscribe to camera feed

        # lane detection publishers

        # LED
        
        # ROI vertices
        
        # define other variables as needed

    def undistort_image(self, **kwargs):
        # add your code here
        pass

    def preprocess_image(self, **kwargs):
        # add your code here
        pass
    
    def detect_lane_color(self, **kwargs):
        # add your code here
        pass
    
    def detect_lane(self, **kwargs):
        # add your code here
        # potentially useful in question 2.1
        pass
    
    
    def callback(self, **kwargs):
        # add your code here
        
        # convert compressed image to CV2
        
        # undistort image

        # preprocess image

        # detect lanes - 2.1 
        
        # publish lane detection results
        
        # detect lanes and colors - 1.3
        
        # publish undistorted image
        
        # control LEDs based on detected colors

        # anything else you want to add here
        
        pass

    # add other functions as needed

if __name__ == '__main__':
    node = LaneDetectionNode(node_name='lane_detection_node')
    rospy.spin()