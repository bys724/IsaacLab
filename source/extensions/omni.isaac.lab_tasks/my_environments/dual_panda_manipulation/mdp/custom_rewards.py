"""커스텀 보상 함수들."""

import torch
from typing import TYPE_CHECKING

from isaaclab.assets import RigidObject, Articulation
from isaaclab.managers import SceneEntityCfg

if TYPE_CHECKING:
    from isaaclab.envs import ManagerBasedRLEnv


def object_ee_distance(
    env: "ManagerBasedRLEnv", 
    threshold: float = 0.05,
    asset_cfg: SceneEntityCfg = SceneEntityCfg("cube")
) -> torch.Tensor:
    """엔드이펙터와 물체 사이 거리 기반 보상.
    
    Args:
        env: 환경 인스턴스
        threshold: 거리 임계값
        asset_cfg: 물체 자산 설정
        
    Returns:
        보상 텐서
    """
    # 큐브 위치
    asset: RigidObject = env.scene[asset_cfg.name]
    cube_pos = asset.data.root_pos_w[:, :3]  # [num_envs, 3]
    
    # 왼쪽 로봇 엔드이펙터 위치
    left_robot: Articulation = env.scene["panda_left"]
    left_ee_pos = left_robot.data.body_pos_w[:, left_robot.body_names.index("panda_hand"), :3]
    
    # 오른쪽 로봇 엔드이펙터 위치
    right_robot: Articulation = env.scene["panda_right"]
    right_ee_pos = right_robot.data.body_pos_w[:, right_robot.body_names.index("panda_hand"), :3]
    
    # 각 로봇과 큐브 사이 최소 거리
    left_dist = torch.norm(cube_pos - left_ee_pos, dim=-1)
    right_dist = torch.norm(cube_pos - right_ee_pos, dim=-1)
    
    # 더 가까운 로봇의 거리 사용
    min_dist = torch.min(left_dist, right_dist)
    
    # 거리 기반 보상 (가까울수록 높은 보상)
    reward = 1.0 - torch.tanh(min_dist / threshold)
    
    return reward


def object_lifted(
    env: "ManagerBasedRLEnv",
    minimal_height: float = 0.9,
    asset_cfg: SceneEntityCfg = SceneEntityCfg("cube")
) -> torch.Tensor:
    """물체를 들어올렸을 때 보상.
    
    Args:
        env: 환경 인스턴스
        minimal_height: 최소 높이
        asset_cfg: 물체 자산 설정
        
    Returns:
        보상 텐서
    """
    asset: RigidObject = env.scene[asset_cfg.name]
    cube_height = asset.data.root_pos_w[:, 2]  # [num_envs]
    
    # 높이 초과시 보상
    reward = torch.where(cube_height > minimal_height, 1.0, 0.0)
    
    return reward


def dual_robot_cooperation(
    env: "ManagerBasedRLEnv",
    cooperation_threshold: float = 0.3
) -> torch.Tensor:
    """두 로봇이 협력할 때 보상.
    
    Args:
        env: 환경 인스턴스
        cooperation_threshold: 협력 거리 임계값
        
    Returns:
        보상 텐서
    """
    # 왼쪽 로봇 엔드이펙터
    left_robot: Articulation = env.scene["panda_left"]
    left_ee_pos = left_robot.data.body_pos_w[:, left_robot.body_names.index("panda_hand"), :3]
    
    # 오른쪽 로봇 엔드이펙터
    right_robot: Articulation = env.scene["panda_right"]
    right_ee_pos = right_robot.data.body_pos_w[:, right_robot.body_names.index("panda_hand"), :3]
    
    # 두 엔드이펙터 사이 거리
    ee_dist = torch.norm(left_ee_pos - right_ee_pos, dim=-1)
    
    # 적절한 거리 유지시 보상
    reward = torch.exp(-torch.abs(ee_dist - cooperation_threshold))
    
    return reward