import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Int64

class MessageSubscriber(Node):
    def __init__(self):
        super().__init__('message_subscriber')
        self.name_subscription = self.create_subscription(
            String,
            'name_listener',
            self.name_callback,
            10)
        self.id_subscription = self.create_subscription(
            Int64,
            'num_listener',
            self.id_callback,
            10)
        self.name = None
        self.student_id = None
        self.name_subscription
        self.id_subscription

    def name_callback(self, msg):
        self.name = msg.data
        self.print_message()

    def id_callback(self, msg):
        self.student_id = msg.data
        self.print_message()

    def print_message(self):
        if self.name is not None and self.student_id is not None:
            message = f"quack quack! Duck cadet {self.name} checking in with ID {self.student_id}!"
            self.get_logger().info(message)

def main(args=None):
    rclpy.init(args=args)
    message_subscriber = MessageSubscriber()
    
    rclpy.spin(message_subscriber)
    message_subscriber.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()