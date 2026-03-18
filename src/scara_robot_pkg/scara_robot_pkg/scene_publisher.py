#!/usr/bin/env python3

import math
from typing import Dict, List, Optional, Tuple

import rclpy
from gazebo_msgs.msg import ModelStates
from geometry_msgs.msg import Pose
from geometry_msgs.msg import Quaternion
from moveit_msgs.msg import CollisionObject, PlanningScene
from moveit_msgs.srv import ApplyPlanningScene
from rclpy.node import Node
from shape_msgs.msg import SolidPrimitive


class ScenePublisher(Node):
    def __init__(self) -> None:
        super().__init__('scene_publisher')

        self.declare_parameter('planning_frame', 'world')
        self.declare_parameter('dynamic_model_names', ['pcb1', 'chip1'])
        self.declare_parameter('dynamic_update_hz', 5.0)

        self._planning_frame = self.get_parameter('planning_frame').get_parameter_value().string_value
        self._dynamic_names = [
            str(name)
            for name in self.get_parameter('dynamic_model_names').get_parameter_value().string_array_value
        ]
        self._update_period = 1.0 / max(
            1.0,
            float(self.get_parameter('dynamic_update_hz').get_parameter_value().double_value),
        )

        self._apply_scene_client = self.create_client(ApplyPlanningScene, '/apply_planning_scene')
        self._model_states_sub = self.create_subscription(
            ModelStates,
            '/gazebo/model_states',
            self._on_model_states,
            20,
        )

        self._static_sent = False
        self._name_to_index: Dict[str, int] = {}
        self._latest_dynamic_poses: Dict[str, Pose] = {}
        self._last_dynamic_stamp = self.get_clock().now()

        self._bootstrap_timer = self.create_timer(1.0, self._bootstrap)
        self._dynamic_timer = self.create_timer(self._update_period, self._publish_dynamic_objects)

        self.get_logger().info('Scene publisher started. Waiting for /apply_planning_scene.')

    def _bootstrap(self) -> None:
        if self._static_sent:
            self._bootstrap_timer.cancel()
            return

        if self._planning_scene_pub.get_subscription_count() == 0:
            self.get_logger().info('Waiting for /planning_scene subscriber...')
            return

        static_objects = self._build_static_objects()
        self._publish_scene_diff(static_objects)
        self._static_sent = True
        self.get_logger().info('Static station objects published to MoveIt planning scene.')

    def _build_static_objects(self) -> List[CollisionObject]:
        # Pedestal from scara_conveyor_gazebo.launch.py and pedestal.urdf
        pedestal_pose = Pose()
        pedestal_pose.position.x = -1.0
        pedestal_pose.position.y = 0.0
        pedestal_pose.position.z = 0.35

        pedestal = self._make_cylinder_object(
            object_id='station_pedestal',
            radius=0.12,
            height=0.7,
            pose=pedestal_pose,
        )

        pedestal_block_pose = Pose()
        pedestal_block_pose.position.x = -1.0
        pedestal_block_pose.position.y = 0.0
        pedestal_block_pose.position.z = 0.75

        pedestal_block = self._make_box_object(
            object_id='station_pedestal_top',
            size_xyz=(0.25, 0.25, 0.1),
            pose=pedestal_block_pose,
        )

        # Conveyor deck footprints approximated as planning boxes.
        belt1_pose = Pose()
        belt1_pose.position.x = 0.0
        belt1_pose.position.y = 0.0
        belt1_pose.position.z = 0.741

        belt1 = self._make_box_object(
            object_id='station_conveyor_1',
            size_xyz=(0.425, 1.2, 0.04),
            pose=belt1_pose,
        )

        belt2_pose = Pose()
        belt2_pose.position.x = -1.0
        belt2_pose.position.y = -1.0
        belt2_pose.position.z = 0.741
        belt2_pose.orientation = self._quaternion_from_yaw(-1.5708)

        belt2 = self._make_box_object(
            object_id='station_conveyor_2',
            size_xyz=(0.425, 1.2, 0.04),
            pose=belt2_pose,
        )

        return [pedestal, pedestal_block, belt1, belt2]

    def _on_model_states(self, msg: ModelStates) -> None:
        if not self._name_to_index:
            self._name_to_index = {name: idx for idx, name in enumerate(msg.name)}

        for model_name in self._dynamic_names:
            idx = self._name_to_index.get(model_name)
            if idx is None:
                try:
                    idx = msg.name.index(model_name)
                    self._name_to_index[model_name] = idx
                except ValueError:
                    continue

            if idx >= len(msg.pose):
                continue

            self._latest_dynamic_poses[model_name] = msg.pose[idx]

    def _publish_dynamic_objects(self) -> None:
        if not self._static_sent:
            return

        now = self.get_clock().now()
        if (now - self._last_dynamic_stamp).nanoseconds < int(self._update_period * 1e9):
            return

        objects: List[CollisionObject] = []

        pcb_pose = self._latest_dynamic_poses.get('pcb1')
        if pcb_pose is not None:
            objects.append(
                self._make_box_object(
                    object_id='dynamic_pcb1',
                    # Approximated from scaled mesh envelope.
                    size_xyz=(0.0575, 0.1015, 0.0095),
                    pose=pcb_pose,
                )
            )

        chip_pose = self._latest_dynamic_poses.get('chip1')
        if chip_pose is not None:
            objects.append(
                self._make_box_object(
                    object_id='dynamic_chip1',
                    # Approximated from scaled mesh envelope.
                    size_xyz=(0.035, 0.035, 0.0045),
                    pose=chip_pose,
                )
            )

        if not objects:
            self.get_logger().warn(
                'Waiting for pcb1/chip1 in /gazebo/model_states before publishing dynamic scene objects.',
                throttle_duration_sec=5.0,
            )
            return

        self._publish_scene_diff(objects)
        self._last_dynamic_stamp = now

    def _apply_scene(self, collision_objects: List[CollisionObject]) -> bool:
        pass

    def _publish_scene_diff(self, collision_objects: List[CollisionObject]) -> None:
        msg = PlanningScene()
        msg.is_diff = True
        msg.world.collision_objects = collision_objects
        self._planning_scene_pub.publish(msg)

    def _make_box_object(self, object_id: str, size_xyz: Tuple[float, float, float], pose: Pose) -> CollisionObject:
        obj = CollisionObject()
        obj.header.frame_id = self._planning_frame
        obj.id = object_id

        primitive = SolidPrimitive()
        primitive.type = SolidPrimitive.BOX
        primitive.dimensions = [float(size_xyz[0]), float(size_xyz[1]), float(size_xyz[2])]

        obj.primitives = [primitive]
        obj.primitive_poses = [pose]
        obj.operation = CollisionObject.ADD
        return obj

    def _make_cylinder_object(self, object_id: str, radius: float, height: float, pose: Pose) -> CollisionObject:
        obj = CollisionObject()
        obj.header.frame_id = self._planning_frame
        obj.id = object_id

        primitive = SolidPrimitive()
        primitive.type = SolidPrimitive.CYLINDER
        primitive.dimensions = [float(height), float(radius)]

        obj.primitives = [primitive]
        obj.primitive_poses = [pose]
        obj.operation = CollisionObject.ADD
        return obj

    @staticmethod
    def _quaternion_from_yaw(yaw: float) -> Quaternion:
        half = yaw / 2.0
        q = Quaternion()
        q.x = 0.0
        q.y = 0.0
        q.z = math.sin(half)
        q.w = math.cos(half)
        return q


def main() -> None:
    rclpy.init()
    node = ScenePublisher()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
