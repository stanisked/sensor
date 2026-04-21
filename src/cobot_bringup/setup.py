from setuptools import setup
import os
from glob import glob

package_name = 'cobot_bringup'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='you',
    maintainer_email='you@email.com',
    description='Cobot bringup',
    license='MIT',

    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),

        # 🔥 ВАЖНО: launch файлы
        (os.path.join('share', package_name, 'launch'),
            glob('launch/*.py')),

        # 🔥 конфиги (если есть)
        (os.path.join('share', package_name, 'config'),
            glob('config/*.yaml')),
    ],

    entry_points={
        'console_scripts': [],
    },
)
