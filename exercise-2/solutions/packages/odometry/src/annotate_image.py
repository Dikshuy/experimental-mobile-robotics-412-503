#!/usr/bin/env python3

import os
import rospy
from duckietown.dtros import DTROS, NodeType
from sensor_msgs.msg import CompressedImage
import cv2
from cv_bridge import CvBridge

class CameraReaderNode(DTROS):
    def __init__(self, node_name):
        super(CameraReaderNode, self).__init__(node_name=node_name, node_type=NodeType.VISUALIZATION)

        # topics
        self._vehicle_name = os.environ['VEHICLE_NAME']
        self._camera_topic = f"/{self._vehicle_name}/camera_node/image/compressed"

        # bridge between OpenCV and ROS
        self._bridge = CvBridge()
        
        # create window
        self._window = "camera-reader"
        cv2.namedWindow(self._window, cv2.WINDOW_AUTOSIZE)
        
        # construct subscriber and publisher
        self.sub = rospy.Subscriber(self._camera_topic, CompressedImage, self.callback)
        self.pub = rospy.Publisher(f'/{self._vehicle_name}/annotated_image/compressed', CompressedImage, queue_size=1)

    def callback(self, msg):
        # Convert JPEG bytes to CV image
        image = self._bridge.compressed_imgmsg_to_cv2(msg)
        
        # Print image size (height and width)
        height, width = image.shape[:2]
        rospy.loginfo(f"Image size: {width}x{height}")
        
        # Convert to grayscale
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Annotate the image
        annotation = f"Duck {self._vehicle_name} says, 'Cheese! Capturing {width}x{height} – quack-tastic!'"
        cv2.putText(gray_image, 
                    annotation, 
                    (10, height - 20),  # Position near bottom-left
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    0.5,  # Font scale
                    255,  # White color for grayscale
                    1)  # Thickness
        
        # Display frame
        cv2.imshow(self._window, gray_image)
        cv2.waitKey(1)
        
        # Publish annotated grayscale image
        annotated_msg = self._bridge.cv2_to_compressed_imgmsg(gray_image)
        self.pub.publish(annotated_msg)

if __name__ == '__main__':
    # Create the node
    node = CameraReaderNode(node_name='annotate_image_node')
    
    # Keep spinning
    rospy.spin()