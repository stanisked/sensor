from setuptools import setup

package_name = 'cobot_driver'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='elwis',
    maintainer_email='stanislavked@gmail.com',
    description='Cobot driver',
    license='MIT',
    entry_points={
        'console_scripts': [
            'servo_bridge = cobot_driver.servo_bridge_node:main',
            'wheel_driver = cobot_driver.wheel_driver_node:main',
        ],
    },
)
