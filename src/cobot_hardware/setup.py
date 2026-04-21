from setuptools import setup
import os

package_name = 'cobot_hardware'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Важно: регистрация плагина для ros2_control
        (os.path.join('share', 'ament_index', 'resource_index', 'ros2_control__hardware_interface'),
            ['resource/servo_hardware']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='elwis',
    maintainer_email='stanislavked@gmail.com',
    description='Cobot hardware',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        ],
        'hardware_interface': [
            'cobot_hardware/servo_hardware = cobot_hardware.servo_hardware:ServoHardware',
        ],
    },
)
