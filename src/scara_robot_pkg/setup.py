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
        ('share/' + package_name + '/launch', glob('launch/*.py') + glob('launch/*.launch')),
        ('share/' + package_name + '/config', glob('config/*')),
        ('share/' + package_name + '/urdf', glob('urdf/*')),
        ('share/' + package_name + '/worlds', glob('worlds/*')),
        ('share/' + package_name + '/models/conveyor_belt_2', glob('models/conveyor_belt_2/*.*')),
        ('share/' + package_name + '/models/conveyor_belt_2/meshes', glob('models/conveyor_belt_2/meshes/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='maxrec',
    maintainer_email='maxrec@todo.todo',
    description='SCARA robot pick and place pipeline',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'scene_publisher = scara_robot_pkg.scene_publisher:main',
            'pick_place_cycle = scara_robot_pkg.pick_place_cycle:main',
        ],
    },
)
