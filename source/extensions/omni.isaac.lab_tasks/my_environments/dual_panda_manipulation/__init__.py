# Copyright (c) 2025, Dual Panda Manipulation Environment
# 듀얼 Panda 로봇 조작 환경

"""듀얼 Panda 로봇을 이용한 테이블탑 조작 환경."""

import gymnasium as gym
from . import agents

# 환경 등록
gym.register(
    id="Isaac-DualPanda-Manipulation-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    kwargs={
        "env_cfg_entry_point": f"{__name__}.env_cfg:DualPandaManipulationEnvCfg",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:DualPandaPPORunnerCfg",
    },
    disable_env_checker=True,
)

# ROS2 제어용 환경 (헤드리스 모드 비활성화)
gym.register(
    id="Isaac-DualPanda-Manipulation-ROS2-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv", 
    kwargs={
        "env_cfg_entry_point": f"{__name__}.env_cfg:DualPandaManipulationEnvCfg_ROS2",
    },
    disable_env_checker=True,
)

# 플레이/테스트용 환경 (적은 환경 수)
gym.register(
    id="Isaac-DualPanda-Manipulation-Play-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    kwargs={
        "env_cfg_entry_point": f"{__name__}.env_cfg:DualPandaManipulationEnvCfg_PLAY",
    },
    disable_env_checker=True,
)