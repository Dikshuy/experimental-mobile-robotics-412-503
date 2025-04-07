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

class ApriltagNode(DTROS):

    def __init__(self, node_name):
        super(ApriltagNode, self).__init__(node_name=node_name, node_type=NodeType.CONTROL)

        # add your code here

        
        # call navigation control node
        self.nav = NavigationControl()

        # initialize dt_apriltag detector
        self.detector = dt_apriltags.Detector(families="tag36h11")
        self.tag_size = 0.065
        self.camera_parameters = None
        self._vehicle_name = os.environ['VEHICLE_NAME']
        self.last_tag_id = -1

        self.tagid_to_led = {
            -1: "white",
            169: "red",
            153: "blue",
            94: "green"
        }

        # subscribe to camera feed
        self.img_topic = f"/{self._vehicle_name}/camera_node/image/compressed"
        camera_info_topic = f"/{self._vehicle_name}/camera_node/camera_info"
        self.img_sub = rospy.Subscriber(self.img_topic, CompressedImage, self.camera_callback, queue_size = 1)
        self.camera_info_sub = rospy.Subscriber(camera_info_topic, CameraInfo, self.camera_info_callback,  queue_size=1)

        # define other variables as needed
        self.led_publisher = rospy.Publisher(f'/{self._vehicle_name}/led_control', String,queue_size=10)
        self.tag_detection_pub = rospy.Publisher("/" + self._vehicle_name + '/tag_detections/compressed', CompressedImage, queue_size=1)

        self.sign_to_led(self.last_tag_id)

    def init_image_sub(self):
        self.camera_info_sub = rospy.Subscriber(
            self.img_topic,
            CompressedImage,
            self.camera_callback,
            queue_size=1
        )

    def camera_info_callback(self, msg):
        self.camera_calibration = msg

        # print("== Calibrating Camera ==")

        # currRawImage_height = img.shape[0]
        # currRawImage_width = img.shape[1]
        currRawImage_height = 640
        currRawImage_width = 480

        scale_matrix = np.ones(9)
        if self.camera_calibration.height != currRawImage_height or self.camera_calibration.width != currRawImage_width:
            scale_width = float(currRawImage_width) / self.camera_calibration.width
            scale_height = float(currRawImage_height) / self.camera_calibration.height
            scale_matrix[0] *= scale_width
            scale_matrix[2] *= scale_width
            scale_matrix[4] *= scale_height
            scale_matrix[5] *= scale_height

        self.tag_size = 0.065 #rospy.get_param("~tag_size", 0.065)
        rect_K, _ = cv2.getOptimalNewCameraMatrix(
            (np.array(self.camera_calibration.K)*scale_matrix).reshape((3, 3)),
            self.camera_calibration.D,
            (640,480),
            1.0
        )
        self.camera_parameters = (rect_K[0, 0], rect_K[1, 1], rect_K[0, 2], rect_K[1, 2])


        try:
            self.subscriberCameraInfo.shutdown()
            self.safeToRunProgram = True
            # print("== Camera Info Subscriber successfully killed ==")
        except BaseException:
            pass

    def sign_to_led(self, tag_id):
        if tag_id is None:
            return self.tagid_to_led[self.last_tag_id]
        self.last_tag_id = tag_id
        return self.tagid_to_led[tag_id]
        

    def process_image(self, col_img):        
        grey_img = cv2.cvtColor(col_img, cv2.COLOR_BGR2GRAY)
        return grey_img[: 2 * len(col_img) // 3]
        # self.col_img = col_img[: 2 * len(col_img) // 3]

    def publish_augmented_img(self, **kwargs):
        pass

    def detect_line(self, image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        red_ranges = {'lower': np.array([0, 150, 50]), 'upper': np.array([10, 255, 255])}
        

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

    def execute_red_line_behavior(self):
        self.nav.stop(4)
        self.nav.move_straight(0.3)
        self.img_sub.unregister()
        self.init_image_sub()

    def set_led_pattern(self, pattern):
        msg = String()
        msg.data = pattern
        self.led_publisher.publish(msg)

    def detect_tag(self, gray_img, col_img):
        if self.camera_parameters is None:
            return None
        tags = self.detector.detect(gray_img)

        if len(tags) == 0:
            self.dist_from_april = 999/2
            self.error_from_april = 0

            msg = CompressedImage()
            msg.header.stamp = rospy.Time.now()
            msg.format = "jpeg"
            msg.data = np.array(cv2.imencode('.jpg', col_img)[1]).tobytes()
            self.tag_detection_pub.publish(msg)
            return None
        
        closest = 0
        for tag in tags:
            # extract the bounding box (x, y)-coordinates for the AprilTag
            # and convert each of the (x, y)-coordinate pairs to integers
            (ptA, ptB, ptC, ptD) = tag.corners
            diff = abs(ptA[0] - ptB[0])
            ptB = (int(ptB[0]), int(ptB[1]))
            ptC = (int(ptC[0]), int(ptC[1]))
            ptD = (int(ptD[0]), int(ptD[1]))
            ptA = (int(ptA[0]), int(ptA[1]))
            

            # draw the bounding box of the AprilTag detection
            line_col = (125, 125, 0)
            cv2.line(col_img, ptA, ptB, line_col, 2)
            cv2.line(col_img, ptB, ptC, line_col, 2)
            cv2.line(col_img, ptC, ptD, line_col, 2)
            cv2.line(col_img, ptD, ptA, line_col, 2)

            

            # get the center (x, y)-coordinates of the AprilTag
            (cX, cY) = (int(tag.center[0]), int(tag.center[1]))

            # draw the tag id on the image
            txt_col = (25, 25, 200)
            tag_id = tag.tag_id
            cv2.putText(col_img, str(tag_id), (cX - 9, cY + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.5, txt_col, 2)

            # if multiple seen, return the closest tag id
            if diff > closest:                
                closest = diff
                closest_tag_id = tag.tag_id
                
        # publish the image with the tag id and box to a custom topic
        msg = CompressedImage()
        msg.header.stamp = rospy.Time.now()
        msg.format = "jpeg"
        msg.data = np.array(cv2.imencode('.jpg', col_img)[1]).tobytes()
        self.tag_detection_pub.publish(msg)

        return int(closest_tag_id)

    def camera_callback(self, msg):
        data_arr = np.frombuffer(msg.data, np.uint8)
        col_img = cv2.imdecode(data_arr, cv2.IMREAD_COLOR)
        gray_img = self.process_image(col_img)

        # detect apriltag logic
        tag_id = self.detect_tag(gray_img, col_img)
        led_pattern = self.sign_to_led(tag_id)
        self.set_led_pattern(led_pattern)
        rospy.loginfo(f"{tag_id}, {led_pattern}")
        
        self.nav.publish_velocity(0.5, 0)

        # redline logic
        stopline_detected, distance = self.detect_line(col_img)
        if stopline_detected and distance < 30:
            self.execute_red_line_behavior()
            self.last_tag_id = -1


if __name__ == '__main__':
    # create the node
    node = ApriltagNode(node_name='apriltag_detector_node')
    rospy.spin()
    
