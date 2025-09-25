# Copyright (c) 2025, Dual Panda Manipulation Environment
"""듀얼 Panda 로봇 조작 환경 설정."""

from __future__ import annotations

import math
from dataclasses import MISSING

import isaaclab.sim as sim_utils
from isaaclab.assets import ArticulationCfg, AssetBaseCfg, RigidObjectCfg
from isaaclab.envs import ManagerBasedRLEnvCfg
from isaaclab.managers import ActionTermCfg as ActionTerm
from isaaclab.managers import CurriculumTermCfg as CurrTerm
from isaaclab.managers import EventTermCfg as EventTerm
from isaaclab.managers import ObservationGroupCfg as ObsGroup
from isaaclab.managers import ObservationTermCfg as ObsTerm
from isaaclab.managers import RewardTermCfg as RewTerm
from isaaclab.managers import SceneEntityCfg
from isaaclab.managers import TerminationTermCfg as DoneTerm
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.sensors import CameraCfg, ContactSensorCfg
from isaaclab.sim import SimulationCfg
from isaaclab.utils import configclass
from isaaclab.utils.assets import ISAAC_NUCLEUS_DIR

# Import MDP 함수들
from . import mdp

# Franka Panda 설정 가져오기
from isaaclab_assets import FRANKA_PANDA_CFG


##
# Scene definition
##

@configclass
class DualPandaSceneCfg(InteractiveSceneCfg):
    """듀얼 Panda 로봇과 테이블, 카메라가 포함된 씬 설정."""
    
    # 지면
    ground = AssetBaseCfg(
        prim_path="/World/ground",
        spawn=sim_utils.GroundPlaneCfg(size=(10.0, 10.0))
    )
    
    # 조명
    dome_light = AssetBaseCfg(
        prim_path="/World/Light",
        spawn=sim_utils.DomeLightCfg(intensity=2000.0, color=(0.8, 0.8, 0.8))
    )
    
    # 테이블
    table = AssetBaseCfg(
        prim_path="{ENV_REGEX_NS}/Table",
        spawn=sim_utils.CuboidCfg(
            size=(1.5, 0.8, 0.75),
            rigid_props=sim_utils.RigidBodyPropertiesCfg(kinematic_enabled=True),
            visual_material=sim_utils.PreviewSurfaceCfg(diffuse_color=(0.6, 0.4, 0.2))
        ),
        init_state=AssetBaseCfg.InitialStateCfg(pos=(0.0, 0.0, 0.375))
    )
    
    # 왼쪽 Panda 로봇
    panda_left: ArticulationCfg = FRANKA_PANDA_CFG.replace(
        prim_path="{ENV_REGEX_NS}/PandaLeft",
        init_state=ArticulationCfg.InitialStateCfg(
            pos=(-0.75, -0.3, 0.75),  # 테이블 왼쪽 가장자리 바깥
            rot=(0.0, 0.0, 0.7071, 0.7071),  # 90도 회전하여 테이블을 향하게
            joint_pos={
                "panda_joint1": 0.0,
                "panda_joint2": -0.5,
                "panda_joint3": 0.0,
                "panda_joint4": -2.0,
                "panda_joint5": 0.0,
                "panda_joint6": 2.5,
                "panda_joint7": 0.0,
                "panda_finger_joint.*": 0.04,
            },
        )
    )
    
    # 오른쪽 Panda 로봇
    panda_right: ArticulationCfg = FRANKA_PANDA_CFG.replace(
        prim_path="{ENV_REGEX_NS}/PandaRight", 
        init_state=ArticulationCfg.InitialStateCfg(
            pos=(0.75, -0.3, 0.75),  # 테이블 오른쪽 가장자리 바깥
            rot=(0.0, 0.0, -0.7071, 0.7071),  # -90도 회전하여 테이블을 향하게
            joint_pos={
                "panda_joint1": 0.0,
                "panda_joint2": -0.5,
                "panda_joint3": 0.0,
                "panda_joint4": -2.0,
                "panda_joint5": 0.0,
                "panda_joint6": 2.5,
                "panda_joint7": 0.0,
                "panda_finger_joint.*": 0.04,
            },
        )
    )
    
    # ZED2i 스테레오 카메라 (탑뷰) - 카메라 사용시 --enable_cameras 플래그 필요
    # zed_camera = CameraCfg(
    #     prim_path="{ENV_REGEX_NS}/ZED2i",
    #     update_period=0.033,  # 30 FPS
    #     height=720,
    #     width=1280,
    #     data_types=["rgb", "depth", "semantic_segmentation"],
    #     spawn=sim_utils.PinholeCameraCfg(
    #         focal_length=2.8,
    #         focus_distance=1.5,
    #         horizontal_aperture=4.0,
    #         clipping_range=(0.1, 10.0),
    #     ),
    #     offset=CameraCfg.OffsetCfg(
    #         pos=(0.0, 0.0, 2.0),  # 테이블 위 2m
    #         rot=(0.0, 1.0, 0.0, 0.0),  # 아래 보기
    #         convention="ros",
    #     ),
    # )
    
    # 조작할 큐브
    cube = RigidObjectCfg(
        prim_path="{ENV_REGEX_NS}/Cube",
        spawn=sim_utils.CuboidCfg(
            size=(0.05, 0.05, 0.05),
            rigid_props=sim_utils.RigidBodyPropertiesCfg(),
            mass_props=sim_utils.MassPropertiesCfg(mass=0.1),
            collision_props=sim_utils.CollisionPropertiesCfg(),
            visual_material=sim_utils.PreviewSurfaceCfg(diffuse_color=(0.0, 1.0, 0.0)),
        ),
        init_state=RigidObjectCfg.InitialStateCfg(
            pos=(0.0, 0.0, 0.8),  # 테이블 위
            rot=(1.0, 0.0, 0.0, 0.0),
        ),
    )
    
    # 접촉 센서 (옵션) - 사용시 로봇 설정에 activate_contact_sensors=True 필요
    # contact_sensor_left = ContactSensorCfg(
    #     prim_path="{ENV_REGEX_NS}/PandaLeft/panda_hand",
    #     update_period=0.01,
    #     history_length=3,
    # )
    
    # contact_sensor_right = ContactSensorCfg(
    #     prim_path="{ENV_REGEX_NS}/PandaRight/panda_hand", 
    #     update_period=0.01,
    #     history_length=3,
    # )


##
# MDP settings
##

@configclass
class ActionsCfg:
    """액션 설정."""
    
    # 왼쪽 팔 제어
    left_arm_joint_pos = mdp.JointPositionActionCfg(
        asset_name="panda_left",
        joint_names=["panda_joint.*"],
        scale=0.5,
        use_default_offset=True,
    )
    
    # 오른쪽 팔 제어  
    right_arm_joint_pos = mdp.JointPositionActionCfg(
        asset_name="panda_right",
        joint_names=["panda_joint.*"],
        scale=0.5,
        use_default_offset=True,
    )
    
    # 왼쪽 그리퍼
    left_gripper = mdp.BinaryJointPositionActionCfg(
        asset_name="panda_left",
        joint_names=["panda_finger_joint.*"],
        open_command_expr={"panda_finger_joint.*": 0.04},
        close_command_expr={"panda_finger_joint.*": 0.0},
    )
    
    # 오른쪽 그리퍼
    right_gripper = mdp.BinaryJointPositionActionCfg(
        asset_name="panda_right",
        joint_names=["panda_finger_joint.*"],
        open_command_expr={"panda_finger_joint.*": 0.04},
        close_command_expr={"panda_finger_joint.*": 0.0},
    )


@configclass
class ObservationsCfg:
    """관측 설정."""
    
    @configclass
    class PolicyCfg(ObsGroup):
        """정책 학습을 위한 관측."""
        
        # 로봇 상태
        left_joint_pos = ObsTerm(func=mdp.joint_pos_rel, params={"asset_cfg": SceneEntityCfg("panda_left")})
        left_joint_vel = ObsTerm(func=mdp.joint_vel_rel, params={"asset_cfg": SceneEntityCfg("panda_left")})
        right_joint_pos = ObsTerm(func=mdp.joint_pos_rel, params={"asset_cfg": SceneEntityCfg("panda_right")})
        right_joint_vel = ObsTerm(func=mdp.joint_vel_rel, params={"asset_cfg": SceneEntityCfg("panda_right")})
        
        # 큐브 위치
        cube_position = ObsTerm(func=mdp.root_pos_w, params={"asset_cfg": SceneEntityCfg("cube")})
        
        # 액션
        actions = ObsTerm(func=mdp.last_action)
        
        def __post_init__(self):
            self.enable_corruption = True
            self.concatenate_terms = True
    
    # 정책 관측
    policy: PolicyCfg = PolicyCfg()


@configclass 
class RewardsCfg:
    """보상 설정."""
    
    # 큐브 도달 보상
    reaching_cube = RewTerm(func=mdp.object_ee_distance, params={"threshold": 0.05}, weight=1.0)
    
    # 큐브 들기 보상
    lifting_cube = RewTerm(func=mdp.object_lifted, params={"minimal_height": 0.9}, weight=5.0)
    
    # 액션 페널티
    action_penalty = RewTerm(func=mdp.action_l2, weight=-0.01)
    
    # 관절 속도 페널티 (왼쪽 로봇)
    left_joint_vel_penalty = RewTerm(
        func=mdp.joint_vel_l2, 
        params={"asset_cfg": SceneEntityCfg("panda_left")},
        weight=-0.001
    )
    
    # 관절 속도 페널티 (오른쪽 로봇)  
    right_joint_vel_penalty = RewTerm(
        func=mdp.joint_vel_l2,
        params={"asset_cfg": SceneEntityCfg("panda_right")}, 
        weight=-0.001
    )


@configclass
class TerminationsCfg:
    """종료 조건."""
    
    # 시간 초과
    time_out = DoneTerm(func=mdp.time_out, time_out=True)
    
    # 큐브 떨어뜨림
    cube_dropped = DoneTerm(
        func=mdp.root_height_below_minimum,
        params={"minimum_height": 0.5, "asset_cfg": SceneEntityCfg("cube")}
    )


@configclass
class EventsCfg:
    """이벤트 설정."""
    
    # 매 에피소드 시작시 큐브 위치 랜덤화
    reset_cube_position = EventTerm(
        func=mdp.reset_root_state_uniform,
        mode="reset",
        params={
            "pose_range": {"x": (-0.2, 0.2), "y": (-0.1, 0.1), "z": (0.0, 0.0)},
            "velocity_range": {},
            "asset_cfg": SceneEntityCfg("cube"),
        },
    )


##
# Environment configuration
##

@configclass
class DualPandaManipulationEnvCfg(ManagerBasedRLEnvCfg):
    """듀얼 Panda 조작 환경 설정."""
    
    # Scene
    scene = DualPandaSceneCfg(num_envs=4096, env_spacing=3.0)
    
    # MDP
    actions = ActionsCfg()
    observations = ObservationsCfg() 
    rewards = RewardsCfg()
    terminations = TerminationsCfg()
    events = EventsCfg()
    
    # 시뮬레이션
    sim = SimulationCfg(dt=1.0 / 60.0, render_interval=4)
    
    def __post_init__(self):
        """후처리."""
        self.decimation = 4
        self.episode_length_s = 10.0
        self.sim.physics_material = sim_utils.RigidBodyMaterialCfg(
            friction_combine_mode="multiply",
            restitution_combine_mode="multiply",
            static_friction=1.0,
            dynamic_friction=1.0,
        )


@configclass
class DualPandaManipulationEnvCfg_PLAY(DualPandaManipulationEnvCfg):
    """플레이/테스트용 환경 (적은 환경 수)."""
    
    def __post_init__(self):
        super().__post_init__()
        # 플레이용 설정
        self.scene.num_envs = 1
        self.sim.render_interval = 1


@configclass
class DualPandaManipulationEnvCfg_ROS2(DualPandaManipulationEnvCfg):
    """ROS2 제어용 환경."""
    
    def __post_init__(self):
        super().__post_init__()
        # ROS2용 설정
        self.scene.num_envs = 1
        self.sim.render_interval = 1
        self.viewer = True  # GUI 활성화