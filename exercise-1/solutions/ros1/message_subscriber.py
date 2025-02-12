#!/usr/bin/env python

import rospy
from std_msgs.msg import String, Int32

class Subscriber:
    def __init__(self):
        self.name = ""
        self.student_id = 0
        self.name_received = False
        self.id_received = False
        
        rospy.init_node('duck_subscriber', anonymous=True)

        rospy.Subscriber('name_listener', String, self.name_callback)
        rospy.Subscriber('num_listener', Int32, self.id_callback)
    
    def name_callback(self, data):
        self.name = data.data
        self.name_received = True
        self.print_message()
    
    def id_callback(self, data):
        self.student_id = data.data
        self.id_received = True
        self.print_message()
    
    def print_message(self):
        if self.name_received and self.id_received:
            print(f"quack quack! Duck cadet {self.name} checking in with ID {self.student_id}!")

if __name__ == '__main__':
    subscriber = Subscriber()
    rospy.spin()