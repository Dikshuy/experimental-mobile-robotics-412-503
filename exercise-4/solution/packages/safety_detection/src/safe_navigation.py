#!/usr/bin/env python3
import dt_apriltags
from cv_bridge import CvBridge
import cv2
import tf

import os
import rospy
from duckietown.dtros import DTROS, NodeType
from duckietown_msgs.msg import BoolStamped, VehicleCorners
from geometry_msgs.msg import Point32
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

# potentially useful for part 2 of exercise 4

# import required libraries
import rospy
from duckietown.dtros import DTROS, NodeType

class SafeNavigationNode(DTROS):

    def __init__(self, node_name):
        super(SafeNavigationNode, self).__init__(node_name=node_name, node_type=NodeType.LOCALIZATION)

        # add your code here
        self.last_stamp = rospy.Time.now()
        self.process_frequency = 2
        self.circlepattern_dims = [7, 3]

        self.manuvering = False
        self.manuver_state = 0
        # Once again, terrible way to approximate time
        self.state_time = 0
        self.nav = NavigationControl()

        
        #Parameters for the blob detector, passed to `SimpleBlobDetector <https://docs.opencv.org/4.3.0/d0/d7a/classcv_1_1SimpleBlobDetector.html>`_
        self.blobdetector_min_area = 10
        self.blobdetector_min_dist_between_blobs = 2


        self.cbParametersChanged() 

        self.bridge = CvBridge()

        # call navigation control node

        # subscribe to camera feed
        img_topic = f"""/{os.environ['VEHICLE_NAME']}/camera_node/image/compressed"""
        self.img_sub = rospy.Subscriber(img_topic, CompressedImage, self.image_callback, queue_size = 1)

        # define other variables as needed
        self.pub_centers = rospy.Publisher("/{}/duckiebot_detection_node/centers".format(os.environ['VEHICLE_NAME']), VehicleCorners, queue_size=1)
        self.pub_circlepattern_image = rospy.Publisher("/{}/duckiebot_detection_node/detection_image/compressed".format(os.environ['VEHICLE_NAME']), CompressedImage, queue_size=1)
        self.pub_detection = rospy.Publisher("/{}/duckiebot_detection_node/detection".format(os.environ['VEHICLE_NAME']), BoolStamped, queue_size=1)
        self.log("Detection Initialization completed.")

    def cbParametersChanged(self):

        self.publish_duration = rospy.Duration.from_sec(1.0 / self.process_frequency)
        params = cv2.SimpleBlobDetector_Params()
        params.minArea = self.blobdetector_min_area
        params.minDistBetweenBlobs = self.blobdetector_min_dist_between_blobs
        self.simple_blob_detector = cv2.SimpleBlobDetector_create(params)

    def detect_bot(self, image_cv):
        """
        Callback for processing a image which potentially contains a back pattern. Processes the image only if
        sufficient time has passed since processing the previous image (relative to the chosen processing frequency).

        The pattern detection is performed using OpenCV's `findCirclesGrid <https://docs.opencv.org/2.4/modules/calib3d/doc/camera_calibration_and_3d_reconstruction.html?highlight=solvepnp#findcirclesgrid>`_ function.

        Args:
            image_msg (:obj:`sensor_msgs.msg.CompressedImage`): Input image

        """
        now = rospy.Time.now()
        if now - self.last_stamp < self.publish_duration:
            return
        else:
            self.last_stamp = now

        (detection, centers) = cv2.findCirclesGrid(
            image_cv,
            patternSize=tuple(self.circlepattern_dims),
            flags=cv2.CALIB_CB_SYMMETRIC_GRID,
            blobDetector=self.simple_blob_detector,
        )

        # if the detection is successful add the information about it,
        # otherwise publish a message saying that it was unsuccessful
        if detection > 0:
            points_list = []
            for point in centers:
                center = Point32()
                center.x = point[0, 0]
                center.y = point[0, 1]
                center.z = 0
                points_list.append(center)

        if self.pub_circlepattern_image.get_num_connections() > 0:
            cv2.drawChessboardCorners(image_cv, tuple(self.circlepattern_dims), centers, detection)
            image_msg_out = self.bridge.cv2_to_compressed_imgmsg(image_cv)
            self.pub_circlepattern_image.publish(image_msg_out)
        
        if detection > 0:
            return np.max(centers) - np.min(centers) > 250
        return False

    def manuver_around_bot(self):
        print("MANUEVERING...")
        self.state_time += 1
        turn_angle = 10
        turn_time = 12
        straight_time = 50
        if self.state_time < 5:
            return 0, 0

        # wait for 1 second
        if self.manuver_state == 0:
            if self.state_time > 25:
                self.manuver_state += 1
                self.state_time = 0
            vel = 0
            twist = 0
        # turn to face other lane
        elif self.manuver_state == 1:
            if self.state_time > turn_time:
                self.manuver_state += 1
                self.state_time = 0
            vel = -0.25
            twist = turn_angle
        # drive into other lane 
        elif self.manuver_state == 2:
            if self.state_time > straight_time:
                self.manuver_state += 1
                self.state_time = 0
            vel = 0.25
            twist = 0
        # turn to drive past other bot
        elif self.manuver_state == 3:
            if self.state_time > turn_time:
                self.manuver_state += 1
                self.state_time = 0
            vel = 0.25
            twist = -turn_angle
        # drive past other bot
        elif self.manuver_state == 4:
            if self.state_time > straight_time:
                self.manuver_state += 1
                self.state_time = 0
            vel = 0.25
            twist = 0
        # turn back to face proper lane
        elif self.manuver_state == 5:
            if self.state_time > turn_time:
                self.manuver_state += 1
                self.state_time = 0
            vel = 0.25
            twist = -turn_angle
        # drive into proper lane
        elif self.manuver_state == 6:
            if self.state_time > straight_time:
                self.manuver_state += 1
                self.state_time = 0
            vel = 0.25
            twist = 0
        # turn to face proper direction
        elif self.manuver_state == 7:
            if self.state_time > turn_time:
                self.manuver_state += 1
                self.state_time = 0
            vel = 0.25
            twist = turn_angle
        # end manuver
        else:
            self.manuvering = False
            self.state_time = 0
            self.manuver_state = 0
            vel = 0.2
            twist = 0
        
        return vel, twist

    def image_callback(self, msg):
        image_cv = self.bridge.compressed_imgmsg_to_cv2(msg, "bgr8")
        bot_detected = self.detect_bot(image_cv)
        vel = 0.3
        twist = 0

        if bot_detected or self.manuvering:
            self.manuvering = True
            vel, twist = self.manuver_around_bot()

        # print(vel, twist)
        self.nav.publish_velocity(vel, twist)


if __name__ == '__main__':
    # create the node
    node = SafeNavigationNode(node_name='safe_nav_node')
    rospy.spin()
