import rclpy
from rclpy.node import Node
from std_msgs.msg import Int64

class IdPublisher(Node):
    def __init__(self):
        super().__init__('id_publisher')
        self.publisher_ = self.create_publisher(Int64, 'num_listener', 10)
        self.timer = self.create_timer(1.0, self.timer_callback)
        self.student_id = 12345

    def timer_callback(self):
        msg = Int64()
        msg.data = self.student_id
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: {msg.data}')

def main(args=None):
    rclpy.init(args=args)
    id_publisher = IdPublisher()
    
    rclpy.spin(id_publisher)
    id_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()