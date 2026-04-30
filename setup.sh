#!/bin/bash

# Quick setup script for cobot ROS2 integration

set -e

echo "======================================"
echo "COBOT ROS2 Quick Setup"
echo "======================================"

WHEEL_PORT="${WHEEL_PORT:-/dev/ttyCH341_motors}"
LIDAR_PORT="${LIDAR_PORT:-/dev/ttyUSB0}"
SERVO_PORT="${SERVO_PORT:-/dev/ttyCH341_servo}"
CAMERA_URL="${CAMERA_URL:-http://192.168.1.100:81/stream}"

echo ""
echo "Configuration:"
echo "  Wheel Port:  $WHEEL_PORT"
echo "  LiDAR Port:  $LIDAR_PORT"
echo "  Servo Port:  $SERVO_PORT"
echo "  Camera URL:  $CAMERA_URL"
echo ""

# Check if running with sudo
if [ "$EUID" -eq 0 ]; then
   echo "Setting port permissions..."
   chmod 666 "$WHEEL_PORT" 2>/dev/null || echo "  Warning: Could not access $WHEEL_PORT"
   chmod 666 "$LIDAR_PORT" 2>/dev/null || echo "  Warning: Could not access $LIDAR_PORT"
   chmod 666 "$SERVO_PORT" 2>/dev/null || echo "  Warning: Could not access $SERVO_PORT"
else
   echo "Note: Run with sudo to set port permissions:"
   echo "  sudo chmod 666 $WHEEL_PORT $LIDAR_PORT $SERVO_PORT"
fi

echo ""
echo "Building workspace..."
cd ~/cobot_ws
colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release

echo ""
echo "Setup complete!"
echo ""
echo "To start the robot, run:"
echo "  source ~/cobot_ws/install/setup.bash"
echo "  ros2 launch cobot_bringup robot.launch.py"
echo ""
