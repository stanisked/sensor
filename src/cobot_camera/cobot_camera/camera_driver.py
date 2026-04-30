#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import threading
import urllib.request
import numpy as np

class CameraDriver(Node):
    """ESP32-CAM driver for ROS2."""

    def __init__(self):
        super().__init__('camera_driver')

        # Параметры
        self.declare_parameter('camera_url', 'http://192.168.1.100:81/stream')
        self.declare_parameter('frame_rate', 30)
        self.declare_parameter('frame_id', 'camera')

        self.camera_url = self.get_parameter('camera_url').value
        self.frame_rate = self.get_parameter('frame_rate').value
        self.frame_id = self.get_parameter('frame_id').value

        self.get_logger().info(f"Camera URL: {self.camera_url}")
        self.get_logger().info(f"Frame rate: {self.frame_rate} FPS")

        # CvBridge для конвертации OpenCV в ROS
        self.bridge = CvBridge()

        # Publisher
        self.image_pub = self.create_publisher(Image, '/camera/image_raw', 10)

        # Поток для захвата
        self.running = True
        self.cap = None
        self.capture_thread = threading.Thread(target=self.capture_loop, daemon=True)
        self.capture_thread.start()

        self.get_logger().info("Camera driver started")

    def connect_camera(self):
        """Подключение к потоку ESP32-CAM."""
        try:
            self.cap = cv2.VideoCapture(self.camera_url)
            if not self.cap.isOpened():
                self.get_logger().error(f"Failed to open camera stream: {self.camera_url}")
                return False

            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            self.get_logger().info("Connected to camera stream")
            return True
        except Exception as e:
            self.get_logger().error(f"Error connecting to camera: {e}")
            return False

    def capture_loop(self):
        """Основной цикл захвата кадров."""
        reconnect_attempts = 0
        max_reconnect_attempts = 5
        reconnect_delay = 2.0

        while self.running:
            if self.cap is None or not self.cap.isOpened():
                if reconnect_attempts < max_reconnect_attempts:
                    self.get_logger().warning(
                        f"Attempting to reconnect... ({reconnect_attempts + 1}/{max_reconnect_attempts})"
                    )
                    if self.connect_camera():
                        reconnect_attempts = 0
                    else:
                        reconnect_attempts += 1
                        rclpy.time.sleep_for(reconnect_delay)
                        continue
                else:
                    self.get_logger().error("Max reconnection attempts reached")
                    break

            try:
                ret, frame = self.cap.read()

                if not ret:
                    self.get_logger().warning("Failed to read frame")
                    self.cap.release()
                    self.cap = None
                    reconnect_attempts += 1
                    continue

                # Конвертация в ROS Image
                msg = self.bridge.cv2_to_imgmsg(frame, encoding="bgr8")
                msg.header.frame_id = self.frame_id
                msg.header.stamp = self.get_clock().now().to_msg()

                self.image_pub.publish(msg)
                self.get_logger().debug(f"Published frame: {frame.shape}")

            except Exception as e:
                self.get_logger().error(f"Error in capture loop: {e}")
                if self.cap is not None:
                    self.cap.release()
                self.cap = None
                reconnect_attempts += 1

            # Контроль frame rate
            rclpy.time.sleep_for(1.0 / self.frame_rate)

    def destroy_node(self):
        """Очистка ресурсов."""
        self.running = False
        if self.cap is not None:
            self.cap.release()
        if self.capture_thread is not None:
            self.capture_thread.join(timeout=2.0)
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = CameraDriver()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()