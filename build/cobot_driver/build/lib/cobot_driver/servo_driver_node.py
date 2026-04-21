#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64MultiArray

import time
import threading

from scservo_sdk import *

PORT = "/dev/ttyCH341_servo"
BAUDRATE = 1000000

CENTER_TICKS = 2048
TICKS_PER_REV = 4096
TICK_PER_DEG = TICKS_PER_REV / 360.0

JOINT_IDS = [1, 2, 3]

MIN_ANGLE = {
    1: -180.0,
    2: -100.0,
    3: -120.0,
}

MAX_ANGLE = {
    1: 180.0,
    2: 100.0,
    3: 120.0,
}


def angle_to_ticks(angle_deg):
    return int(CENTER_TICKS + angle_deg * TICK_PER_DEG)


def ticks_to_angle(pos_ticks):
    return (pos_ticks - CENTER_TICKS) / TICK_PER_DEG


class ServoDriverNode(Node):

    def __init__(self):
        super().__init__('servo_driver_node')

        # --- Publishers ---
        self.joint_state_pub = self.create_publisher(
            JointState,
            '/joint_states',
            10
        )

        # --- Subscribers ---
        self.command_sub = self.create_subscription(
            Float64MultiArray,
            '/joint_commands',
            self.command_callback,
            10
        )

        # --- Init hardware ---
        self.portHandler = PortHandler(PORT)
        self.packetHandler = sms_sts(self.portHandler)

        if not self.portHandler.openPort():
            raise RuntimeError("Cannot open port")

        if not self.portHandler.setBaudRate(BAUDRATE):
            raise RuntimeError("Cannot set baudrate")

        self.get_logger().info("Servo bus initialized")

        # Включаем torque
        for sid in JOINT_IDS:
            self.enable_torque(sid, True)

        # состояние
        self.current_positions = [0.0] * len(JOINT_IDS)
        self.lock = threading.Lock()

        # поток
        self.running = True
        self.state_thread = threading.Thread(target=self.state_loop)
        self.state_thread.start()

    # -------------------------
    # Hardware methods
    # -------------------------

    def enable_torque(self, sid, enable=True):
        addr_torque = 40
        self.packetHandler.write1ByteTxRx(
            sid,
            addr_torque,
            1 if enable else 0
        )

    def read_position(self, sid):
        addr_present_pos = 56
        pos, comm_result, error = self.packetHandler.read2ByteTxRx(
            sid,
            addr_present_pos
        )

        if comm_result != COMM_SUCCESS:
            return None

        angle = ticks_to_angle(pos)

        # защита от мусора
        if angle < -360 or angle > 360:
            return None

        return angle

    def safe_read(self, sid, retries=3):
        for _ in range(retries):
            angle = self.read_position(sid)
            if angle is not None:
                return angle
        return None

    def move_joint(self, sid, angle_deg, speed=800, acc=25):

        if sid not in MIN_ANGLE:
            return

        # ограничение
        angle_deg = max(MIN_ANGLE[sid], min(MAX_ANGLE[sid], angle_deg))

        pos_ticks = angle_to_ticks(angle_deg)

        try:
            self.packetHandler.WritePosEx(
                sid,
                pos_ticks,
                int(speed),
                int(acc)
            )
        except AttributeError:
            addr_pos = 42
            self.packetHandler.write2ByteTxRx(sid, addr_pos, pos_ticks)

    # -------------------------
    # ROS callbacks
    # -------------------------

    def command_callback(self, msg):
        """
        Ожидаем:
        [j1, j2, j3] в градусах
        """

        if len(msg.data) != len(JOINT_IDS):
            self.get_logger().warn("Wrong command size")
            return

        for i, sid in enumerate(JOINT_IDS):
            angle = msg.data[i]
            self.move_joint(sid, angle)

    # -------------------------
    # State publishing loop
    # -------------------------

    def state_loop(self):
        rate = 10  # Hz

        while self.running:
            joint_msg = JointState()
            joint_msg.header.stamp = self.get_clock().now().to_msg()
            joint_msg.name = [f"joint_{i+1}" for i in range(len(JOINT_IDS))]

            positions = []

            for i, sid in enumerate(JOINT_IDS):
                angle = self.safe_read(sid)

                with self.lock:
                    if angle is None:
                        angle = self.current_positions[i]
                    else:
                        self.current_positions[i] = angle

                positions.append(angle)

            joint_msg.position = positions
            self.joint_state_pub.publish(joint_msg)

            time.sleep(1.0 / rate)

    # -------------------------

    def destroy_node(self):
        self.running = False
        self.state_thread.join()

        for sid in JOINT_IDS:
            self.enable_torque(sid, False)

        self.portHandler.closePort()

        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)

    node = ServoDriverNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
