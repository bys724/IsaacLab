"""커스텀 액션 함수들."""

import torch
from typing import TYPE_CHECKING

from isaaclab.assets import Articulation
from isaaclab.managers import ActionTerm
from isaaclab.managers import ActionTermCfg

if TYPE_CHECKING:
    from isaaclab.envs import ManagerBasedEnv


class DualArmCoordinatedActionCfg(ActionTermCfg):
    """두 팔을 조율된 방식으로 제어하는 액션 설정."""
    
    left_asset_name: str = "panda_left"
    """왼쪽 로봇 자산 이름."""
    
    right_asset_name: str = "panda_right"
    """오른쪽 로봇 자산 이름."""
    
    joint_names: list[str] = ["panda_joint.*"]
    """제어할 관절 이름 패턴."""
    
    scale: float = 1.0
    """액션 스케일."""
    
    offset: float = 0.0
    """액션 오프셋."""
    
    coordination_mode: str = "mirror"
    """조율 모드: 'mirror', 'symmetric', 'independent'"""


class DualArmCoordinatedAction(ActionTerm):
    """두 팔을 조율된 방식으로 제어하는 액션."""
    
    cfg: DualArmCoordinatedActionCfg
    
    def __init__(self, cfg: DualArmCoordinatedActionCfg, env: "ManagerBasedEnv"):
        super().__init__(cfg, env)
        
        # 왼쪽과 오른쪽 로봇 가져오기
        self.left_robot: Articulation = env.scene[cfg.left_asset_name]
        self.right_robot: Articulation = env.scene[cfg.right_asset_name]
        
        # 액션 차원 설정
        self._action_dim = len(self.left_robot.joint_names)
        
    @property
    def action_dim(self) -> int:
        """액션 차원."""
        return self._action_dim
    
    def process_actions(self, actions: torch.Tensor) -> None:
        """액션 처리 및 적용.
        
        Args:
            actions: 액션 텐서 [num_envs, action_dim]
        """
        # 액션 스케일링
        scaled_actions = actions * self.cfg.scale + self.cfg.offset
        
        if self.cfg.coordination_mode == "mirror":
            # 미러 모드: 오른팔은 왼팔의 거울상
            left_actions = scaled_actions
            right_actions = scaled_actions.clone()
            right_actions[:, [0, 2, 4, 6]] *= -1  # y축 기준 미러링
            
        elif self.cfg.coordination_mode == "symmetric":
            # 대칭 모드: 같은 동작
            left_actions = scaled_actions
            right_actions = scaled_actions
            
        elif self.cfg.coordination_mode == "independent":
            # 독립 모드: 액션을 반으로 나눔
            half_dim = self._action_dim // 2
            left_actions = scaled_actions[:, :half_dim]
            right_actions = scaled_actions[:, half_dim:]
            
        else:
            raise ValueError(f"Unknown coordination mode: {self.cfg.coordination_mode}")
        
        # 로봇에 액션 적용
        self.left_robot.set_joint_position_target(left_actions)
        self.right_robot.set_joint_position_target(right_actions)


class SynchronizedGripperActionCfg(ActionTermCfg):
    """동기화된 그리퍼 액션 설정."""
    
    left_asset_name: str = "panda_left"
    """왼쪽 로봇 자산 이름."""
    
    right_asset_name: str = "panda_right" 
    """오른쪽 로봇 자산 이름."""
    
    gripper_joint_names: list[str] = ["panda_finger_joint.*"]
    """그리퍼 관절 이름."""
    
    open_position: float = 0.04
    """그리퍼 열린 위치."""
    
    close_position: float = 0.0
    """그리퍼 닫힌 위치."""


class SynchronizedGripperAction(ActionTerm):
    """동기화된 그리퍼 액션."""
    
    cfg: SynchronizedGripperActionCfg
    
    def __init__(self, cfg: SynchronizedGripperActionCfg, env: "ManagerBasedEnv"):
        super().__init__(cfg, env)
        
        self.left_robot: Articulation = env.scene[cfg.left_asset_name]
        self.right_robot: Articulation = env.scene[cfg.right_asset_name]
        
        self._action_dim = 2  # 왼쪽, 오른쪽 그리퍼
        
    @property
    def action_dim(self) -> int:
        """액션 차원."""
        return self._action_dim
    
    def process_actions(self, actions: torch.Tensor) -> None:
        """그리퍼 액션 처리.
        
        Args:
            actions: 이진 액션 텐서 [num_envs, 2] (0: 닫기, 1: 열기)
        """
        num_envs = actions.shape[0]
        
        # 왼쪽 그리퍼
        left_gripper_pos = torch.where(
            actions[:, 0:1] > 0.5,
            torch.full((num_envs, 2), self.cfg.open_position, device=actions.device),
            torch.full((num_envs, 2), self.cfg.close_position, device=actions.device)
        )
        
        # 오른쪽 그리퍼
        right_gripper_pos = torch.where(
            actions[:, 1:2] > 0.5,
            torch.full((num_envs, 2), self.cfg.open_position, device=actions.device),
            torch.full((num_envs, 2), self.cfg.close_position, device=actions.device)
        )
        
        # 그리퍼 위치 설정
        self.left_robot.set_joint_position_target(left_gripper_pos, joint_ids=self.left_robot.gripper_indices)
        self.right_robot.set_joint_position_target(right_gripper_pos, joint_ids=self.right_robot.gripper_indices)