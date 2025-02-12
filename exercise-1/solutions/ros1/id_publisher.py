#!/usr/bin/env python

import rospy
from std_msgs.msg import Int32

def id_publisher():
    rospy.init_node('id_publisher', anonymous=True)
    pub = rospy.Publisher('num_listener', Int32, queue_size=10)
    rate = rospy.Rate(10)
    
    while not rospy.is_shutdown():
        student_id = 14
        pub.publish(student_id)
        rate.sleep()

if __name__ == '__main__':
    try:
        id_publisher()
    except rospy.ROSInterruptException:
        pass