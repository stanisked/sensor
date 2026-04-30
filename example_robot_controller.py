#!/usr/bin/env python3

"""
Пример скрипта для управления роботом
"""

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node


class RobotController(Node):
    """Простой контроллер для управления роботом."""

    def __init__(self):
        super().__init__('robot_controller')
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 1)

    def move_forward(self, speed=0.5):
        """Движение вперёд."""
        msg = Twist()
        msg.linear.x = speed
        self.publisher.publish(msg)
        self.get_logger().info(f"Moving forward: {speed}")

    def move_backward(self, speed=0.5):
        """Движение назад."""
        msg = Twist()
        msg.linear.x = -speed
        self.publisher.publish(msg)
        self.get_logger().info(f"Moving backward: {speed}")

    def turn_left(self, angular_speed=0.5):
        """Поворот влево."""
        msg = Twist()
        msg.angular.z = angular_speed
        self.publisher.publish(msg)
        self.get_logger().info(f"Turning left: {angular_speed}")

    def turn_right(self, angular_speed=0.5):
        """Поворот вправо."""
        msg = Twist()
        msg.angular.z = -angular_speed
        self.publisher.publish(msg)
        self.get_logger().info(f"Turning right: {angular_speed}")

    def stop(self):
        """Остановка."""
        msg = Twist()
        self.publisher.publish(msg)
        self.get_logger().info("Stopping")


def main():
    rclpy.init()
    controller = RobotController()

    try:
        # Простой пример: прямоугольник
        controller.move_forward(0.5)
        rclpy.spin_once(controller, timeout_sec=2)

        controller.turn_left(0.5)
        rclpy.spin_once(controller, timeout_sec=1)

        controller.move_forward(0.5)
        rclpy.spin_once(controller, timeout_sec=2)

        controller.stop()
        rclpy.spin_once(controller, timeout_sec=0.5)

    finally:
        controller.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
