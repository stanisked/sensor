#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import serial
import time

PORT = "/dev/ttyCH341_motors"
BAUD = 115200

SPEED_STEP = 10
SPEED_MIN = 0
SPEED_MAX = 255


class WheelDriverNode(Node):

    def __init__(self):
        super().__init__('wheel_driver')

        self.declare_parameter('port', PORT)
        self.declare_parameter('baud', BAUD)
        self.declare_parameter('speed_step', SPEED_STEP)
        self.declare_parameter('speed_min', SPEED_MIN)
        self.declare_parameter('speed_max', SPEED_MAX)

        self.port = self.get_parameter('port').value
        self.baud = self.get_parameter('baud').value
        self.speed_step = self.get_parameter('speed_step').value
        self.speed_min = self.get_parameter('speed_min').value
        self.speed_max = self.get_parameter('speed_max').value

        self.get_logger().info(f"Opening {self.port} @ {self.baud}")
        self.ser = serial.Serial(self.port, self.baud, timeout=0.1)

        # Send stop command
        self.send_cmd("s")

        self.speed = 180  # default speed

        # Subscriber to cmd_vel
        self.sub = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_vel_callback,
            10
        )

        self.get_logger().info("Wheel driver started")

    def send_cmd(self, cmd, speed=None):
        """Send command to ESP32."""
        if speed is not None:
            line = f"V {speed}\n"
            self.ser.write(line.encode("ascii"))
            self.ser.flush()
        line = cmd + "\n"
        self.ser.write(line.encode("ascii"))
        self.ser.flush()
        self.get_logger().debug(f"TX: {line.strip()}")

    def cmd_vel_callback(self, msg):
        linear_x = msg.linear.x
        angular_z = msg.angular.z

        # Simple differential drive logic
        if linear_x > 0:
            if angular_z > 0:
                # forward left
                self.send_cmd("l", int(self.speed * (1 - angular_z)))
                self.send_cmd("r", int(self.speed))
            elif angular_z < 0:
                # forward right
                self.send_cmd("l", int(self.speed))
                self.send_cmd("r", int(self.speed * (1 + angular_z)))
            else:
                # forward
                self.send_cmd("f", self.speed)
        elif linear_x < 0:
            # backward
            self.send_cmd("b", self.speed)
        else:
            if angular_z > 0:
                # rotate left
                self.send_cmd("l", self.speed)
                self.send_cmd("r", -self.speed)  # assuming protocol supports negative
            elif angular_z < 0:
                # rotate right
                self.send_cmd("l", -self.speed)
                self.send_cmd("r", self.speed)
            else:
                # stop
                self.send_cmd("s")

    def destroy_node(self):
        self.send_cmd("s")
        self.ser.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = WheelDriverNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()