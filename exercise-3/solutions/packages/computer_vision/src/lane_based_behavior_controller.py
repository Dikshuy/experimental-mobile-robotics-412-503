#!/usr/bin/env python3

import os
import rospy
import numpy as np
from duckietown.dtros import DTROS, NodeType
from sensor_msgs.msg import CompressedImage
from std_msgs.msg import String, Bool
import cv2
from cv_bridge import CvBridge
from navigate import NavigationControl

DEBUG = True

class BehaviorController(DTROS):
    def __init__(self, node_name):
        super(BehaviorController, self).__init__(node_name=node_name, node_type=NodeType.CONTROL)

        self.nav = NavigationControl()
        
        # Initialize camera and lane detection parameters
        self._vehicle_name = os.environ['VEHICLE_NAME']
        self._camera_topic = f"/{self._vehicle_name}/camera_node/image/compressed"
        self._bridge = CvBridge()
        
        # Color ranges in HSV
        self.color_ranges = {
            'blue': {'lower': np.array([100, 150, 50]), 'upper': np.array([140, 255, 255])},
            'red': {'lower': np.array([0, 150, 50]), 'upper': np.array([10, 255, 255])},
            'green': {'lower': np.array([49, 66, 238]), 'upper': np.array([85, 138, 22])}
        }
        
        # LED control publisher ( this needs update, just implemented a basic version)
        self.led_publisher = rospy.Publisher(f'/{self._vehicle_name}/led_control', String,queue_size=10)
        self.debug_pub = rospy.Publisher(f"/{self._vehicle_name}/contour_image/compressed", CompressedImage, queue_size=1)
        self.intersection_pub = rospy.Publisher(f"/{self._vehicle_name}/intersection_detection", Bool, queue_size=1)
        
        # Subscribe to camera feed
        self.init_image_sub()
        
        # State variables
        self.current_color = None
        self.distance_to_line = float('inf')
        self.is_executing_behavior = False

    def init_image_sub(self):
        self.sub = rospy.Subscriber(
            self._camera_topic,
            CompressedImage,
            self.callback,
            queue_size=1
        )
        
    def set_led_pattern(self, pattern):
        msg = String()
        msg.data = pattern
        self.led_publisher.publish(msg)
        
    def detect_line(self, image):
        rospy.loginfo("DETECTING...")
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        for color_name, ranges in self.color_ranges.items():
            mask = cv2.inRange(hsv, ranges['lower'], ranges['upper'])
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                if DEBUG:
                    cv2.drawContours(image, [largest_contour], -1, (0, 255, 0), 3) 
                    contour_img = self._bridge.cv2_to_compressed_imgmsg(image)
                    self.debug_pub.publish(contour_img)
                if cv2.contourArea(largest_contour) > 500:
                    x, y, w, h = cv2.boundingRect(largest_contour)
                    
                    # Estimate distance based on contour position
                    image_height = image.shape[0]
                    distance = (image_height - (y + h)) / image_height
                    
                    return color_name, distance * 100
                    
        return None, float('inf')
    
    def execute_blue_line_behavior(self):
        self.nav.stop(4)
        self.set_led_pattern("right_blink")
        rospy.sleep(1)
        self.nav.turn_right()
        self.is_executing_behavior = False
        self.sub.unregister()
        self.init_image_sub()

        
    def execute_red_line_behavior(self):
        self.nav.stop(4)
        self.nav.move_straight(0.3)
        self.is_executing_behavior = False
        self.sub.unregister()
        self.init_image_sub()
        
    def execute_green_line_behavior(self):
        self.nav.stop(4)
        self.set_led_pattern("left_blink")
        rospy.sleep(1)
        self.nav.turn_left()
        self.is_executing_behavior = False
        self.sub.unregister()
        self.init_image_sub()
        
    def callback(self, msg):
        rospy.loginfo(self.is_executing_behavior)
        if self.is_executing_behavior:
            return
            
        image = self._bridge.compressed_imgmsg_to_cv2(msg)
        
        color, distance = self.detect_line(image)

        self.nav.publish_velocity(0.5, 0)
        
        if color and distance < 30:
            rospy.loginfo(color)
            self.is_executing_behavior = True
            self.intersection_pub.publish(True)
            
            if color == 'blue':
                self.execute_blue_line_behavior()
            elif color == 'red':
                self.execute_red_line_behavior()
            elif color == 'green':
                self.execute_green_line_behavior()
        else:
            self.intersection_pub.publish(False)

if __name__ == '__main__':
    node = BehaviorController(node_name='behavior_controller_node')
    rospy.spin()