from setuptools import find_packages, setup
from glob import glob

package_name = 'scara_robot_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
        ('share/' + package_name + '/config', glob('config/*.yaml')),
        ('share/' + package_name + '/worlds', glob('worlds/*.world')),
        ('share/' + package_name + '/urdf', glob('urdf/*.urdf')),
        ('share/' + package_name + '/rviz', ['rviz/default_view.rviz']),
        ('share/' + package_name + '/meshes', glob('meshes/*')), #include meshes
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='apostolos-ubuntu-pc',
    maintainer_email='apostolos-ubuntu-pc@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'pick_place_cycle = scara_robot_pkg.pick_place_cycle:main',
            'scene_publisher = scara_robot_pkg.scene_publisher:main',
        ],
    },
)
