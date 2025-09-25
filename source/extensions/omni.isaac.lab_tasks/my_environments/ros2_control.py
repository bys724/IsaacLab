#!/usr/bin/env python3
"""ROS2를 통한 듀얼 Panda 제어 예제.

이 스크립트는 ROS2 토픽을 통해 듀얼 Panda 로봇을 제어하는 예제입니다.

사용법:
    # ROS2 환경에서 실행 (Docker 컨테이너 내부)
    ros2 run dual_panda_control ros2_control.py
"""

import sys
import torch
import gymnasium as gym
import numpy as np

# ROS2 imports (선택적 - ROS2 설치시)
try:
    import rclpy
    from rclpy.node import Node
    from sensor_msgs.msg import JointState, Image, PointCloud2
    from std_msgs.msg import Float64MultiArray
    from geometry_msgs.msg import PoseStamped
    ROS2_AVAILABLE = True
except ImportError:
    ROS2_AVAILABLE = False
    print("ROS2를 찾을 수 없습니다. 독립 실행 모드로 전환합니다.")


class DualPandaController:
    """듀얼 Panda 제어기 (ROS2 없이도 동작)."""
    
    def __init__(self, env_id="Isaac-DualPanda-Manipulation-ROS2-v0"):
        """초기화.
        
        Args:
            env_id: 환경 ID
        """
        # 커스텀 환경 import
        import my_environments.dual_panda_manipulation
        
        # 환경 생성
        self.env = gym.make(env_id, num_envs=1)
        self.obs, self.info = self.env.reset()
        
        # 액션 차원
        self.action_dim = self.env.action_space.shape[0]
        self.current_action = torch.zeros(1, self.action_dim, device=self.env.device)
        
        print(f"환경 초기화 완료: {env_id}")
        print(f"액션 차원: {self.action_dim}")
        print(f"관측 차원: {self.env.observation_space.shape}")
    
    def set_joint_positions(self, left_joints, right_joints, left_gripper, right_gripper):
        """관절 위치 설정.
        
        Args:
            left_joints: 왼쪽 팔 관절 각도 (7개)
            right_joints: 오른쪽 팔 관절 각도 (7개)
            left_gripper: 왼쪽 그리퍼 (0: 닫기, 1: 열기)
            right_gripper: 오른쪽 그리퍼 (0: 닫기, 1: 열기)
        """
        # 액션 구성 (7+7+2 = 16차원)
        action = torch.zeros(1, self.action_dim, device=self.env.device)
        action[0, :7] = torch.tensor(left_joints, device=self.env.device)
        action[0, 7:14] = torch.tensor(right_joints, device=self.env.device)
        action[0, 14] = left_gripper
        action[0, 15] = right_gripper
        
        self.current_action = action
    
    def step(self):
        """환경 스텝 실행."""
        self.obs, self.reward, self.terminated, self.truncated, self.info = \
            self.env.step(self.current_action)
        
        # 에피소드 종료시 리셋
        if self.terminated.any() or self.truncated.any():
            self.obs, self.info = self.env.reset()
            print("환경 리셋됨")
        
        return self.obs, self.reward
    
    def get_camera_image(self):
        """카메라 이미지 반환.
        
        Returns:
            RGB 이미지 (있는 경우)
        """
        # 환경에서 카메라 데이터 추출
        if hasattr(self.env.scene, "zed_camera"):
            camera = self.env.scene["zed_camera"]
            if "rgb" in camera.data.output:
                return camera.data.output["rgb"][0].cpu().numpy()
        return None
    
    def close(self):
        """환경 종료."""
        self.env.close()


class DualPandaROS2Node(Node):
    """ROS2 노드 (ROS2 사용 가능시)."""
    
    def __init__(self):
        super().__init__('dual_panda_controller')
        
        # 컨트롤러 생성
        self.controller = DualPandaController()
        
        # 구독자
        self.joint_cmd_sub = self.create_subscription(
            JointState,
            '/dual_panda/joint_commands',
            self.joint_command_callback,
            10
        )
        
        # 발행자
        self.joint_state_pub = self.create_publisher(
            JointState,
            '/dual_panda/joint_states',
            10
        )
        
        self.camera_pub = self.create_publisher(
            Image,
            '/dual_panda/camera/rgb',
            10
        )
        
        # 타이머 (30Hz)
        self.timer = self.create_timer(0.033, self.timer_callback)
        
        self.get_logger().info('듀얼 Panda ROS2 노드 시작됨')
    
    def joint_command_callback(self, msg):
        """관절 명령 콜백.
        
        Args:
            msg: JointState 메시지
        """
        # 관절 위치 추출 (14개 관절 + 2개 그리퍼)
        if len(msg.position) >= 16:
            left_joints = msg.position[:7]
            right_joints = msg.position[7:14]
            left_gripper = msg.position[14]
            right_gripper = msg.position[15]
            
            self.controller.set_joint_positions(
                left_joints, right_joints, 
                left_gripper, right_gripper
            )
    
    def timer_callback(self):
        """주기적 업데이트."""
        # 환경 스텝
        obs, reward = self.controller.step()
        
        # 관절 상태 발행
        joint_state_msg = JointState()
        joint_state_msg.header.stamp = self.get_clock().now().to_msg()
        joint_state_msg.position = obs[0, :16].cpu().numpy().tolist()
        self.joint_state_pub.publish(joint_state_msg)
        
        # 카메라 이미지 발행
        rgb_image = self.controller.get_camera_image()
        if rgb_image is not None:
            image_msg = Image()
            image_msg.header.stamp = self.get_clock().now().to_msg()
            image_msg.height, image_msg.width = rgb_image.shape[:2]
            image_msg.encoding = "rgb8"
            image_msg.data = rgb_image.tobytes()
            self.camera_pub.publish(image_msg)


def standalone_demo():
    """ROS2 없이 독립 실행 데모."""
    
    print("\n독립 실행 모드 시작...")
    controller = DualPandaController()
    
    # 간단한 제어 시퀀스
    sequences = [
        # 초기 자세
        ([0.0, -0.5, 0.0, -2.0, 0.0, 2.5, 0.0],
         [0.0, -0.5, 0.0, -2.0, 0.0, 2.5, 0.0], 1.0, 1.0),
        # 접근
        ([0.2, -0.8, 0.0, -1.8, 0.0, 2.2, 0.0],
         [-0.2, -0.8, 0.0, -1.8, 0.0, 2.2, 0.0], 1.0, 1.0),
        # 잡기
        ([0.2, -0.8, 0.0, -1.8, 0.0, 2.2, 0.0],
         [-0.2, -0.8, 0.0, -1.8, 0.0, 2.2, 0.0], 0.0, 0.0),
        # 들어올리기
        ([0.2, -0.3, 0.0, -2.3, 0.0, 2.8, 0.0],
         [-0.2, -0.3, 0.0, -2.3, 0.0, 2.8, 0.0], 0.0, 0.0),
    ]
    
    try:
        for i, (left, right, lg, rg) in enumerate(sequences):
            print(f"\n동작 {i+1}/4 실행 중...")
            controller.set_joint_positions(left, right, lg, rg)
            
            # 50 스텝 실행
            for _ in range(50):
                obs, reward = controller.step()
                
            print(f"보상: {reward.item():.4f}")
        
        print("\n데모 완료!")
        
    finally:
        controller.close()


def main():
    """메인 함수."""
    
    if ROS2_AVAILABLE and "--standalone" not in sys.argv:
        # ROS2 모드
        print("ROS2 모드로 실행합니다...")
        rclpy.init()
        node = DualPandaROS2Node()
        
        try:
            rclpy.spin(node)
        except KeyboardInterrupt:
            pass
        finally:
            node.controller.close()
            node.destroy_node()
            rclpy.shutdown()
    else:
        # 독립 실행 모드
        standalone_demo()


if __name__ == "__main__":
    # Isaac Sim 초기화
    from isaaclab.app import AppLauncher
    
    app_launcher = AppLauncher(headless=False)
    simulation_app = app_launcher.app
    
    try:
        main()
    finally:
        simulation_app.close()