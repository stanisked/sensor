#!/usr/bin/env python3

"""
Simple test script for COBOT components
Usage: python3 test_components.py [component]
  - wheel: Test wheel driver
  - camera: Test camera driver
  - lidar: Test LiDAR driver
  - all: Test all components
"""

import sys
import time
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Image, LaserScan, JointState


class ComponentTester(Node):
    """Test individual ROS2 components."""

    def __init__(self, component='all'):
        super().__init__('component_tester')
        self.component = component
        self.received_data = {
            'camera': False,
            'lidar': False,
            'joint_states': False,
        }

        if component in ('wheel', 'all'):
            self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 1)
            self.get_logger().info("Wheel driver: Ready to send commands")

        if component in ('camera', 'all'):
            self.create_subscription(Image, '/camera/image_raw', self.camera_callback, 1)
            self.get_logger().info("Camera: Listening...")

        if component in ('lidar', 'all'):
            self.create_subscription(LaserScan, '/scan', self.lidar_callback, 1)
            self.get_logger().info("LiDAR: Listening...")

        if component in ('arm', 'all'):
            self.create_subscription(JointState, '/joint_states', self.joint_callback, 1)
            self.get_logger().info("Arm: Listening...")

    def camera_callback(self, msg):
        if not self.received_data['camera']:
            self.received_data['camera'] = True
            self.get_logger().info(
                f"Camera: Received image {msg.width}x{msg.height} "
                f"(encoding: {msg.encoding})"
            )

    def lidar_callback(self, msg):
        if not self.received_data['lidar']:
            self.received_data['lidar'] = True
            self.get_logger().info(
                f"LiDAR: Received {len(msg.ranges)} ranges, "
                f"angle range: {msg.angle_min:.2f} to {msg.angle_max:.2f}"
            )

    def joint_callback(self, msg):
        if not self.received_data['joint_states']:
            self.received_data['joint_states'] = True
            self.get_logger().info(f"Arm: Received joint states: {msg.name}")

    def test_wheel(self):
        """Test wheel movement commands."""
        self.get_logger().info("Testing wheel commands...")

        commands = [
            ("Forward", Twist(linear=rclpy.import_rclpy_structure().geometry_msgs.Vector3(x=0.5))),
            ("Backward", Twist(linear=rclpy.import_rclpy_structure().geometry_msgs.Vector3(x=-0.5))),
            ("Left turn", Twist(angular=rclpy.import_rclpy_structure().geometry_msgs.Vector3(z=0.5))),
            ("Right turn", Twist(angular=rclpy.import_rclpy_structure().geometry_msgs.Vector3(z=-0.5))),
            ("Stop", Twist()),
        ]

        for name, cmd in commands:
            self.get_logger().info(f"  {name}")
            self.cmd_vel_pub.publish(cmd)
            time.sleep(1)


def main():
    component = sys.argv[1] if len(sys.argv) > 1 else 'all'

    if component not in ('wheel', 'camera', 'lidar', 'arm', 'all'):
        print(f"Unknown component: {component}")
        print(__doc__)
        sys.exit(1)

    rclpy.init()
    tester = ComponentTester(component)

    if component in ('wheel', 'all'):
        tester.test_wheel()

    print("\nWaiting 5 seconds for sensor data...")
    start = time.time()
    while time.time() - start < 5:
        rclpy.spin_once(tester, timeout_sec=0.1)

    print("\n=== Test Results ===")
    if component in ('camera', 'all'):
        status = "✓ OK" if tester.received_data['camera'] else "✗ NO DATA"
        print(f"Camera:       {status}")

    if component in ('lidar', 'all'):
        status = "✓ OK" if tester.received_data['lidar'] else "✗ NO DATA"
        print(f"LiDAR:        {status}")

    if component in ('arm', 'all'):
        status = "✓ OK" if tester.received_data['joint_states'] else "✗ NO DATA"
        print(f"Arm:          {status}")

    tester.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
