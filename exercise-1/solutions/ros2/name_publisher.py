import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class NamePublisher(Node):
    def __init__(self):
        super().__init__('name_publisher')
        self.publisher_ = self.create_publisher(String, 'name_listener', 10)
        self.timer = self.create_timer(1.0, self.timer_callback)
        self.name = "Duck"

    def timer_callback(self):
        msg = String()
        msg.data = self.name
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: {msg.data}')

def main(args=None):
    rclpy.init(args=args)
    name_publisher = NamePublisher()
    
    rclpy.spin(name_publisher)
    name_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()