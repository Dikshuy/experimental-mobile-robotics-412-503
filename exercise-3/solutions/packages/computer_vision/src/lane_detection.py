#!/usr/bin/env python3

import os
import rospy
import numpy as np
from duckietown.dtros import DTROS, NodeType
from sensor_msgs.msg import CompressedImage
from std_msgs.msg import String, Float32MultiArray
import cv2
from cv_bridge import CvBridge

class LaneDetectionNode(DTROS):
    def __init__(self, node_name):
        super(LaneDetectionNode, self).__init__(node_name=node_name, node_type=NodeType.PERCEPTION)

        self._vehicle_name = os.environ['VEHICLE_NAME']
        self._camera_topic = f"/{self._vehicle_name}/camera_node/image/compressed"
        
        # Camera calibration parameters (intrinsic matrix and distortion coefficients) - dummy values
        self.camera_matrix = np.array([
            [320.0, 0.0, 320.0],
            [0.0, 320.0, 240.0],
            [0.0, 0.0, 1.0]
        ])
        self.dist_coeffs = np.array([-0.2, 0.1, 0.0, 0.0, 0.0])
        
        # Color detection parameters in HSV
        self.color_ranges = {
            'blue': {'lower': np.array([100, 150, 50]), 'upper': np.array([140, 255, 255])},
            'red': {'lower': np.array([0, 150, 50]), 'upper': np.array([10, 255, 255])},
            'yellow': {'lower': np.array([20, 150, 50]), 'upper': np.array([35, 255, 255])},
            'white': {'lower': np.array([0, 0, 200]), 'upper': np.array([180, 30, 255])}
        }
        
        # Initialize bridge and publishers
        self._bridge = CvBridge()
        self.pub_undistorted = rospy.Publisher(
            f'/{self._vehicle_name}/camera_node/undistorted/compressed',
            CompressedImage,
            queue_size=1
        )

        # lane detection publishers
        self.yellow_lane_pub = rospy.Publisher(
            '~/yellow_lane',
            Float32MultiArray,
            queue_size=1
        )
        self.white_lane_pub = rospy.Publisher(
            '~/white_lane',
            Float32MultiArray,
            queue_size=1
        )
        
        # LED control publisher
        self.led_publisher = rospy.Publisher(f'/{self._vehicle_name}/led_control', String, queue_size=1)
        
        # Subscribe to camera feed
        self.sub = rospy.Subscriber(
            self._camera_topic,
            CompressedImage,
            self.callback,
            queue_size=1,
            buff_size=2**24
        )

        # ROI vertices - dummy
        self.roi_vertices = np.array([
            [0, 480],
            [0, 360],
            [640, 360],
            [640, 480]
        ], dtype=np.int32)
        
        # Processing parameters
        self.process_every_n = 3
        self.frame_count = 0
    
    def undistort_image(self, image):
        h, w = image.shape[:2]
        new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(
            self.camera_matrix, self.dist_coeffs, (w,h), 1, (w,h)
        )
        undistorted = cv2.undistort(
            image, 
            self.camera_matrix, 
            self.dist_coeffs, 
            None, 
            new_camera_matrix
        )
        return undistorted
    
    def preprocess_image(self, image):
        # Resize image
        resized = cv2.resize(image, (640, 480))
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(resized, (5, 5), 0)
        return blurred
    
    def detect_lane_color(self, image):
        # Convert to HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        detected_colors = {}
        
        for color_name, ranges in self.color_ranges.items():
            # Create mask for color
            mask = cv2.inRange(hsv, ranges['lower'], ranges['upper'])
            
            # Find contours
            contours, _ = cv2.findContours(
                mask, 
                cv2.RETR_EXTERNAL, 
                cv2.CHAIN_APPROX_SIMPLE
            )
            
            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                if cv2.contourArea(largest_contour) > 500:
                    x, y, w, h = cv2.boundingRect(largest_contour)
                    
                    cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)

                    detected_colors[color_name] = {
                        'position': (x, y),
                        'dimensions': (w, h),
                        'area': w * h
                    }
        
        return image, detected_colors
    
    def detect_lane(self, image, color_type):
        # Convert to HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Create mask for the specified color
        color_range = self.color_ranges[color_type]
        mask = cv2.inRange(hsv, color_range['lower'], color_range['upper'])
        
        # Apply ROI mask
        roi_mask = np.zeros_like(mask)
        cv2.fillPoly(roi_mask, [self.roi_vertices], 255)
        masked = cv2.bitwise_and(mask, roi_mask)
        
        # Find contours
        contours, _ = cv2.findContours(masked, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None
        
        largest_contour = max(contours, key=cv2.contourArea)
        if cv2.contourArea(largest_contour) < 100:
            return None

        M = cv2.moments(largest_contour)
        if M['m00'] == 0:
            return None
            
        cx = int(M['m10'] / M['m00'])
        cy = int(M['m01'] / M['m00'])
        
        return (cx, cy)
    
    def set_led_color(self, color):
        msg = String()
        msg.data = color
        self.led_publisher.publish(msg)
    
    def save_color_image(self, image, color_name):
        filename = f"/data/{color_name}_lane.jpg"
        cv2.imwrite(filename, image)
        rospy.loginfo(f"Saved {color_name} lane image to {filename}")
    
    def callback(self, msg):
        self.frame_count += 1
        if self.frame_count % self.process_every_n != 0:
            return
        
        # Convert compressed image to CV2
        image = self._bridge.compressed_imgmsg_to_cv2(msg)
        
        # Undistort image
        undistorted = self.undistort_image(image)
        
        # Preprocess image
        processed = self.preprocess_image(undistorted)

        # Detect lanes
        yellow_center = self.detect_lane(processed, 'yellow')
        white_center = self.detect_lane(processed, 'white')
        
        # Publish lane detection results
        if yellow_center:
            yellow_msg = Float32MultiArray()
            yellow_msg.data = yellow_center
            self.yellow_lane_pub.publish(yellow_msg)
            
        if white_center:
            white_msg = Float32MultiArray()
            white_msg.data = white_center
            self.white_lane_pub.publish(white_msg)
        
        # Detect lanes and colors
        result_image, detected_colors = self.detect_lane_color(processed)
        
        # Publish undistorted image
        undistorted_msg = self._bridge.cv2_to_compressed_imgmsg(result_image)
        self.pub_undistorted.publish(undistorted_msg)
        
        # Control LEDs based on detected colors
        if detected_colors:
            primary_color = max(detected_colors.items(), key=lambda x: x[1]['area'])[0]
            self.set_led_color(primary_color)

        # save images
        self.save_color_image(image, "blue")
        self.save_color_image(image, "red")
        self.save_color_image(image, "yellow")

if __name__ == '__main__':
    node = LaneDetectionNode(node_name='lane_detection_node')

    rospy.spin()