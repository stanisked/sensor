import time
import rclpy
from rclpy.node import Node

from hardware_interface import SystemInterface
from hardware_interface import return_type


class ServoHardware(SystemInterface):

    def __init__(self):
        super().__init__()
        self.joint_positions = [0.0, 0.0, 0.0]
        self.joint_commands = [0.0, 0.0, 0.0]

    def configure(self, info):
        self.info = info
        self.get_logger().info("Configuring ServoHardware...")
        return return_type.OK

    def start(self):
        self.get_logger().info("Starting ServoHardware...")
        return return_type.OK

    def stop(self):
        self.get_logger().info("Stopping ServoHardware...")
        return return_type.OK

    def read(self):
        # Пока просто возвращаем текущее состояние
        self.joint_positions = self.joint_commands
        return return_type.OK

    def write(self):
        # Пока просто логируем команды
        self.get_logger().info(f"Sending commands: {self.joint_commands}")
        return return_type.OK
