#!/usr/bin/env python3

import os
import math
import rospy
from duckietown.dtros import DTROS, NodeType
from duckietown_msgs.msg import LEDPattern
from std_msgs.msg import ColorRGBA


class LightController():
    def __init__(self):
        # init the messages to publish to led pattern node
        self._vehicle_name = os.environ['VEHICLE_NAME']
        self.LEDspattern = LEDPattern()
        self.light_color_list = [
                                [1, 0, 0, 1],
                                [1, 0, 0, 1],
                                [1, 0, 0, 1],
                                [1, 0, 0, 1],
                                [1, 0, 0, 1],
                                 ]
        
        # topics
        self.pub_leds = rospy.Publisher(f"/{self._vehicle_name}/led_emitter_node/led_pattern", LEDPattern, queue_size=10)
        self.count = 1
        
    def publish_LED_pattern(self):
        # Publish the LED pattern to the led_emitter_node
        self.LEDspattern.rgb_vals = []
        for i in range(5):
            rgba = ColorRGBA()
            rgba.r = self.light_color_list[i][0]
            rgba.g = self.light_color_list[i][1]
            rgba.b = self.light_color_list[i][2]
            rgba.a = self.light_color_list[i][3]

            self.LEDspattern.rgb_vals.append(rgba)
        self.pub_leds.publish(self.LEDspattern)

    def set_led_color(self, color):
        # Set the color of the LEDs
        color = color.copy()
        if len(color) == 3:
            for i in range(len(self.light_color_list)):
                self.light_color_list[i] = color + [1]
        else:
            self.light_color_list = color
        
        self.publish_LED_pattern()
    
    def time_cycle(self):
        # Cycle through the colors of the LEDs
        for i, light in enumerate(self.light_color_list):
            light = light.copy()
            self.light_color_list[i][0] = light[1]
            self.light_color_list[i][1] = light[2]
            self.light_color_list[i][2] = light[0]
        self.count += 1
        # rospy.loginfo(f"New Light Value: {self.light_color_list[0]}")
        self.publish_LED_pattern()

# just here in case you want to run LED stuff as a stand alone node
class LightControllerNode(DTROS):
    def __init__(self, node_name):
        super(LightControllerNode, self).__init__(node_name=node_name, node_type=NodeType.GENERIC)

        self.light_controller = LightController()


if __name__ == '__main__':
    node = LightControllerNode(node_name='light_controller_node')
    rate = rospy.Rate(0.5)
    #            All lights same col                 Different col/alpha for different lights
    col_list = [[0, 0, 0], [[1, 1, 0, 1],[1, 0, 0, 1],[1, 0, 0, 1],[1, 0, 0, 1],[1, 1, 0, 1],]]
    i = 0
    while not rospy.is_shutdown():
        node.light_controller.time_cycle()
        # i = (i+1) % len(col_list)
        # node.light_controller.set_led_color(col_list[i])
        rospy.sleep(1)
