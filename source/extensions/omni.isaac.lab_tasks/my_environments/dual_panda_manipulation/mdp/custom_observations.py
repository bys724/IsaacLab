"""커스텀 관측 함수들."""

import torch
from typing import TYPE_CHECKING

from isaaclab.assets import Articulation
from isaaclab.sensors import Camera

if TYPE_CHECKING:
    from isaaclab.envs import ManagerBasedRLEnv


def camera_rgb_image(env: "ManagerBasedRLEnv") -> torch.Tensor:
    """ZED2i 카메라의 RGB 이미지 반환.
    
    Args:
        env: 환경 인스턴스
        
    Returns:
        RGB 이미지 텐서 [num_envs, height, width, 3]
    """
    camera: Camera = env.scene["zed_camera"]
    return camera.data.output["rgb"]


def camera_depth_image(env: "ManagerBasedRLEnv") -> torch.Tensor:
    """ZED2i 카메라의 깊이 이미지 반환.
    
    Args:
        env: 환경 인스턴스
        
    Returns:
        깊이 이미지 텐서 [num_envs, height, width]
    """
    camera: Camera = env.scene["zed_camera"]
    return camera.data.output["depth"]


def dual_ee_positions(env: "ManagerBasedRLEnv") -> torch.Tensor:
    """두 로봇의 엔드이펙터 위치.
    
    Args:
        env: 환경 인스턴스
        
    Returns:
        엔드이펙터 위치 텐서 [num_envs, 6] (left_x, left_y, left_z, right_x, right_y, right_z)
    """
    # 왼쪽 로봇 엔드이펙터
    left_robot: Articulation = env.scene["panda_left"]
    left_ee_pos = left_robot.data.body_pos_w[:, left_robot.body_names.index("panda_hand"), :3]
    
    # 오른쪽 로봇 엔드이펙터
    right_robot: Articulation = env.scene["panda_right"]
    right_ee_pos = right_robot.data.body_pos_w[:, right_robot.body_names.index("panda_hand"), :3]
    
    # 결합
    dual_ee_pos = torch.cat([left_ee_pos, right_ee_pos], dim=-1)
    
    return dual_ee_pos


def dual_ee_orientations(env: "ManagerBasedRLEnv") -> torch.Tensor:
    """두 로봇의 엔드이펙터 방향.
    
    Args:
        env: 환경 인스턴스
        
    Returns:
        엔드이펙터 방향 쿼터니언 텐서 [num_envs, 8] 
    """
    # 왼쪽 로봇 엔드이펙터
    left_robot: Articulation = env.scene["panda_left"]
    left_ee_quat = left_robot.data.body_quat_w[:, left_robot.body_names.index("panda_hand"), :]
    
    # 오른쪽 로봇 엔드이펙터
    right_robot: Articulation = env.scene["panda_right"]
    right_ee_quat = right_robot.data.body_quat_w[:, right_robot.body_names.index("panda_hand"), :]
    
    # 결합
    dual_ee_quat = torch.cat([left_ee_quat, right_ee_quat], dim=-1)
    
    return dual_ee_quat


def contact_forces(env: "ManagerBasedRLEnv") -> torch.Tensor:
    """양손의 접촉력.
    
    Args:
        env: 환경 인스턴스
        
    Returns:
        접촉력 텐서 [num_envs, 2]
    """
    # 왼손 접촉력
    left_contact = env.scene["contact_sensor_left"]
    left_force = torch.norm(left_contact.data.net_forces_w, dim=-1).sum(dim=-1)
    
    # 오른손 접촉력
    right_contact = env.scene["contact_sensor_right"]
    right_force = torch.norm(right_contact.data.net_forces_w, dim=-1).sum(dim=-1)
    
    return torch.stack([left_force, right_force], dim=-1)