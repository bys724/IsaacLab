"""듀얼 Panda 조작을 위한 RSL-RL PPO 설정."""

from isaaclab_tasks.utils.wrappers.rsl_rl import RslRlOnPolicyRunnerCfg, RslRlPpoActorCriticCfg, RslRlPpoAlgorithmCfg

# PPO 알고리즘 설정
class DualPandaPPORunnerCfg(RslRlOnPolicyRunnerCfg):
    """듀얼 Panda 조작을 위한 PPO 러너 설정."""
    
    seed = 42
    max_iterations = 1500
    
    # 학습 파라미터
    learn = RslRlOnPolicyRunnerCfg.LearnCfg(
        num_learning_epochs = 5,
        num_mini_batches = 4,
        learning_rate = 3.0e-4,
    )
    
    # 정책 설정
    policy = RslRlPpoActorCriticCfg(
        init_noise_std=1.0,
        actor_hidden_dims=[256, 128, 64],
        critic_hidden_dims=[256, 128, 64],
        activation='elu',
    )
    
    # PPO 알고리즘 설정
    algorithm = RslRlPpoAlgorithmCfg(
        value_loss_coef=1.0,
        use_clipped_value_loss=True,
        clip_param=0.2,
        entropy_coef=0.01,
        num_learning_epochs=5,
        num_mini_batches=4,
        learning_rate=3.0e-4,
        schedule='adaptive',
        gamma=0.99,
        lam=0.95,
        desired_kl=0.01,
        max_grad_norm=1.0,
    )
    
    # 로깅 설정
    experiment_name = "dual_panda_manipulation"
    run_name = ""
    wandb_project = "isaaclab_dual_panda"
    save_interval = 50
    log_interval = 10