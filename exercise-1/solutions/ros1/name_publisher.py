#!/usr/bin/env python

import rospy
from std_msgs.msg import String

def name_publisher():
    rospy.init_node('name_publisher', anonymous=True)
    pub = rospy.Publisher('name_listener', String, queue_size=10)
    rate = rospy.Rate(10)
    
    while not rospy.is_shutdown():
        name = "Duckie"
        pub.publish(name)
        rate.sleep()

if __name__ == '__main__':
    try:
        name_publisher()
    except rospy.ROSInterruptException:
        pass