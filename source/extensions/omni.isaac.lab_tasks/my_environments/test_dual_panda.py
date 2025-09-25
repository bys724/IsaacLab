#!/usr/bin/env python3
"""듀얼 Panda 환경 테스트 스크립트.

사용법:
    # 시각화와 함께 테스트
    ./isaaclab.sh -p source/extensions/omni.isaac.lab_tasks/my_environments/test_dual_panda.py
    
    # 헤드리스 모드로 테스트
    ./isaaclab.sh -p source/extensions/omni.isaac.lab_tasks/my_environments/test_dual_panda.py --headless
    
    # 여러 환경으로 테스트
    ./isaaclab.sh -p source/extensions/omni.isaac.lab_tasks/my_environments/test_dual_panda.py --num_envs 4
"""

import argparse

from isaaclab.app import AppLauncher

# 인자 파싱
parser = argparse.ArgumentParser(description="듀얼 Panda 조작 환경 테스트")
parser.add_argument("--num_envs", type=int, default=1, help="생성할 환경 수")
parser.add_argument("--env_id", type=str, default="Isaac-DualPanda-Manipulation-Play-v0", 
                    help="환경 ID")
parser.add_argument("--test_steps", type=int, default=1000, help="테스트 스텝 수")

# AppLauncher CLI 인자 추가
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()

# Omniverse 앱 실행
app_launcher = AppLauncher(args)
simulation_app = app_launcher.app

"""환경 테스트 코드."""

import torch

# 커스텀 환경 import (등록 실행)
import my_environments.dual_panda_manipulation

from isaaclab.envs import ManagerBasedRLEnv
from my_environments.dual_panda_manipulation.env_cfg import (
    DualPandaManipulationEnvCfg,
    DualPandaManipulationEnvCfg_PLAY
)


def test_random_actions():
    """랜덤 액션으로 환경 테스트."""
    
    print(f"\n{'='*50}")
    print(f"테스트 환경: {args.env_id}")
    print(f"환경 수: {args.num_envs}")
    print(f"{'='*50}\n")
    
    # 환경 설정 생성
    if "Play" in args.env_id:
        env_cfg = DualPandaManipulationEnvCfg_PLAY()
    else:
        env_cfg = DualPandaManipulationEnvCfg()
    
    # 환경 수 및 디바이스 설정
    env_cfg.scene.num_envs = args.num_envs
    env_cfg.sim.device = "cuda:0" if torch.cuda.is_available() else "cpu"
    
    # 환경 생성 (직접 ManagerBasedRLEnv 사용)
    env = ManagerBasedRLEnv(cfg=env_cfg)
    
    # 환경 정보 출력
    print(f"관측 공간: {env.observation_space}")
    print(f"액션 공간: {env.action_space}")
    print(f"액션 차원: {env.action_manager.total_action_dim}")
    print(f"환경 수: {env.num_envs}")
    print(f"에피소드 길이: {env.max_episode_length}")
    
    # 씬에 있는 엔티티 확인
    print(f"\n씬 엔티티:")
    for entity_name in env.scene.keys():
        print(f"  - {entity_name}")
    
    # 액션 매니저 정보 확인
    print(f"\n액션 매니저 정보:")
    for term_name, term in env.action_manager._terms.items():
        print(f"  - {term_name}: dim={term.action_dim}")
    
    # 환경 리셋
    obs, info = env.reset()
    if isinstance(obs, dict):
        print(f"초기 관측 keys: {obs.keys()}")
        for key, value in obs.items():
            if hasattr(value, 'shape'):
                print(f"  - {key}: shape {value.shape}")
    else:
        print(f"초기 관측 shape: {obs.shape}")
    
    # 테스트 루프
    step_count = 0
    episode_count = 0
    episode_returns = torch.zeros(env.num_envs, device=env.device)
    
    print(f"\n랜덤 액션 테스트 시작...")
    print(f"{'='*50}")
    
    for i in range(args.test_steps):
        # 랜덤 액션 샘플링
        actions = torch.randn(env.num_envs, env.action_manager.total_action_dim, device=env.device)
        
        # 스텝 실행
        obs, rewards, terminated, truncated, info = env.step(actions)
        
        # 누적 보상
        episode_returns += rewards
        step_count += 1
        
        # 에피소드 종료 처리
        done = terminated | truncated
        if done.any():
            done_indices = torch.where(done)[0]
            for idx in done_indices:
                episode_count += 1
                print(f"에피소드 {episode_count} 완료 (환경 {idx}): "
                      f"누적 보상 = {episode_returns[idx].item():.2f}")
                episode_returns[idx] = 0.0
        
        # 주기적 상태 출력
        if (i + 1) % 100 == 0:
            print(f"스텝 {i+1}/{args.test_steps}: "
                  f"평균 보상 = {rewards.mean().item():.4f}")
    
    # 환경 종료
    env.close()
    
    print(f"\n{'='*50}")
    print(f"테스트 완료!")
    print(f"총 스텝: {step_count}")
    print(f"완료된 에피소드: {episode_count}")
    print(f"{'='*50}\n")


def test_coordinated_actions():
    """조율된 액션으로 환경 테스트."""
    
    print(f"\n조율된 액션 테스트...")
    
    # 환경 설정 생성
    env_cfg = DualPandaManipulationEnvCfg_PLAY()
    env_cfg.scene.num_envs = 1
    env_cfg.sim.device = "cuda:0" if torch.cuda.is_available() else "cpu"
    
    # 환경 생성
    env = ManagerBasedRLEnv(cfg=env_cfg)
    obs, info = env.reset()
    
    # 간단한 pick and place 시퀀스
    sequences = [
        # 접근
        torch.tensor([[0.0, -0.5, 0.0, -2.0, 0.0, 2.5, 0.0,  # 왼팔
                       0.0, -0.5, 0.0, -2.0, 0.0, 2.5, 0.0,  # 오른팔
                       1.0, 1.0]]),  # 그리퍼 열기
        # 하강
        torch.tensor([[0.0, -0.8, 0.0, -1.5, 0.0, 2.0, 0.0,  # 왼팔
                       0.0, -0.8, 0.0, -1.5, 0.0, 2.0, 0.0,  # 오른팔
                       1.0, 1.0]]),  # 그리퍼 열기
        # 잡기
        torch.tensor([[0.0, -0.8, 0.0, -1.5, 0.0, 2.0, 0.0,  # 왼팔
                       0.0, -0.8, 0.0, -1.5, 0.0, 2.0, 0.0,  # 오른팔
                       0.0, 0.0]]),  # 그리퍼 닫기
        # 들어올리기
        torch.tensor([[0.0, -0.3, 0.0, -2.3, 0.0, 2.8, 0.0,  # 왼팔
                       0.0, -0.3, 0.0, -2.3, 0.0, 2.8, 0.0,  # 오른팔
                       0.0, 0.0]]),  # 그리퍼 닫기
    ]
    
    for seq_idx, target_action in enumerate(sequences):
        print(f"\n시퀀스 {seq_idx + 1}: ", end="")
        
        if seq_idx < 2:
            print("접근 중...")
        elif seq_idx == 2:
            print("잡기...")
        else:
            print("들어올리기...")
        
        # 해당 자세로 천천히 이동
        for _ in range(50):
            obs, rewards, terminated, truncated, _ = env.step(target_action.to(env.device))
            
            if terminated.any() or truncated.any():
                obs, _ = env.reset()
                break
    
    env.close()
    print("조율된 액션 테스트 완료!")


def main():
    """메인 함수."""
    
    # 랜덤 액션 테스트
    test_random_actions()
    
    # 조율된 액션 테스트 (단일 환경에서만)
    if args.num_envs == 1:
        test_coordinated_actions()
    
    # 시뮬레이션 종료
    simulation_app.close()


if __name__ == "__main__":
    main()