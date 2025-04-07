#!/usr/bin/env python3
import dt_apriltags
import cv2
import tf

import os
import rospy
from duckietown.dtros import DTROS, NodeType
import numpy as np

from sensor_msgs.msg import CameraInfo
from sensor_msgs.msg import CompressedImage
from std_msgs.msg import String

# import required libraries
import rospy
from duckietown.dtros import DTROS, NodeType
from navigate_template import NavigationControl

# potentially useful for part 2 of exercise 4

# import required libraries
import rospy
from duckietown.dtros import DTROS, NodeType

class CrossWalkNode(DTROS):

    def __init__(self, node_name):
        super(CrossWalkNode, self).__init__(node_name=node_name, node_type=NodeType.LOCALIZATION)

        # add your code here
        self._vehicle_name = os.environ['VEHICLE_NAME']
        self.detect_crosswalks = True
        self.drive_dist = 0
        # this is a hacky way to do timing, would be better to use rospy.time()....
        # but this works well enough with less effort/vars
        self.stop_time = 0

        self.nav = NavigationControl()

        # subscribe to camera feed
        self.img_topic = f"/{self._vehicle_name}/camera_node/image/compressed"
        self.img_sub = rospy.Subscriber(self.img_topic, CompressedImage, self.camera_callback, queue_size = 1)

    def detect_line(self, image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        red_ranges = {'lower': np.array([100, 150, 50]), 'upper': np.array([140, 255, 255])}
        

        mask = cv2.inRange(hsv, red_ranges['lower'], red_ranges['upper'])
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            if cv2.contourArea(largest_contour) > 500:
                x, y, w, h = cv2.boundingRect(largest_contour)
                
                # Estimate distance based on contour position
                image_height = image.shape[0]
                distance = (image_height - (y + h)) / image_height
                
                return True, distance * 100
                    
        return False, float('inf')

    def detect_ducks(self, image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        duck_ranges = {'lower': np.array([9, 91, 163]), 'upper': np.array([22, 255, 255])}
    
        mask = cv2.inRange(hsv, duck_ranges['lower'], duck_ranges['upper'])
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            return cv2.contourArea(largest_contour) > 500
                    
    

    def camera_callback(self, msg):
        data_arr = np.frombuffer(msg.data, np.uint8)
        col_img = cv2.imdecode(data_arr, cv2.IMREAD_COLOR)
        vel = 0.5

        if self.detect_crosswalks or self.stop_time < 50:
            stopwalk_detection, _ = self.detect_line(col_img)
            if stopwalk_detection:
                self.detect_crosswalks = False
                vel = 0
                self.stop_time += 1
        else:
            if self.detect_ducks(col_img):
                vel = 0
            elif self.drive_dist < 50:
                vel = 0.5
                self.drive_dist += 1
            else:
                self.detect_crosswalks = True
                self.drive_dist = 0
                self.stop_time = 0


        # print(vel)
        self.nav.publish_velocity(vel, 0)


if __name__ == '__main__':
    # create the node
    node = CrossWalkNode(node_name='crosswalk_node')
    rospy.spin()
