#!/usr/bin/env python3

import sys
import math
import rclpy
from rclpy.node import Node

from trajectory_msgs.msg import JointTrajectory
from sensor_msgs.msg import JointState

# путь к библиотеке серв
sys.path.append('/home/elwis/FTServo_Python')

from scservo_sdk.sms_sts import sms_sts
from scservo_sdk.port_handler import PortHandler


PORT = "/dev/ttyCH341_servo"
BAUDRATE = 1000000


class ServoBridge(Node):

    def __init__(self):
        super().__init__('servo_bridge')

        # подключение к сервам
        self.portHandler = PortHandler(PORT)
        self.portHandler.setBaudRate(BAUDRATE)

        self.driver = sms_sts(self.portHandler)

        self.get_logger().info("Servo bridge started")

        # подписка на команды
        self.sub = self.create_subscription(
            JointTrajectory,
            '/arm_controller/joint_trajectory',
            self.callback,
            10
        )

        # publisher joint_states
        self.joint_pub = self.create_publisher(JointState, '/joint_states', 10)

        # таймер чтения (10 Гц)
        self.timer = self.create_timer(0.1, self.read_positions)

        # параметры серв
        self.center = 2048.0
        self.ticks_per_rev = 4096.0
        # параметры speed, acc
        self.declare_parameter('speed', 800)
        self.declare_parameter('acc', 25)

        self.speed = self.get_parameter('speed').value
        self.acc = self.get_parameter('acc').value


    # --- ограничение углов ---
    def clamp(self, val, min_val, max_val):
        return max(min(val, max_val), min_val)

    # --- callback команд ---
    def callback(self, msg):
        if not msg.points:
            return

        positions = msg.points[0].positions

        self.get_logger().info(f"Received: {positions}")

        for i, angle in enumerate(positions):
            servo_id = i + 1

            # ограничение ±90°
            angle = self.clamp(angle, -1.57, 1.57)

            # rad → ticks
            ticks = int(self.center + angle * self.ticks_per_rev / (2.0 * math.pi))

            self.get_logger().info(f"Servo {servo_id} → {ticks}")

            self.driver.WritePosEx(
                servo_id,
                ticks,
                self.speed,  # speed
                self.acc     # acceleration
            )

    # --- чтение позиций ---
    def read_positions(self):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = ['joint_1', 'joint_2', 'joint_3']

        positions = []

        for i in range(3):
            servo_id = i + 1

            pos, _, _ = self.driver.ReadPos(servo_id)

            # ticks → radians
            angle = (pos - self.center) * (2.0 * math.pi / self.ticks_per_rev)

            positions.append(angle)

            # для отладки
            print(f"RAW servo {servo_id}: {pos}")

        msg.position = positions

        self.joint_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = ServoBridge()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
