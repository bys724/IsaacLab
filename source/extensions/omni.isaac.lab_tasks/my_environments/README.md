# 커스텀 환경 모음

IsaacLab을 활용한 커스텀 로봇 환경들입니다.

## 듀얼 Panda 조작 환경

두 대의 Franka Panda 로봇이 협력하여 테이블 위의 물체를 조작하는 환경입니다.

### 주요 특징
- 🤖 **듀얼 암 협력 제어**: 두 대의 Panda 로봇 동시 제어
- 📷 **ZED2i 스테레오 카메라**: RGB, Depth, Semantic Segmentation
- 🌐 **ROS2 원격제어**: 외부 시스템과 통신 가능
- 🎮 **강화학습 지원**: PPO, SAC 등 다양한 알고리즘 적용 가능
- 🔧 **모듈식 설계**: MDP 컴포넌트 쉽게 수정 가능

### 실행 방법

#### 🐳 Docker 환경에서 실행 (권장)

##### Step 1: Docker 컨테이너 시작
```bash
# 프로젝트 루트에서
cd /home/bys/IsaacLab

# 컨테이너 시작 (최초 실행시 이미지 빌드)
python3 docker/container.py start

# 컨테이너 상태 확인
docker ps | grep isaac-lab
```

##### Step 2: 컨테이너 접속
```bash
# 새 터미널에서 컨테이너 접속
python3 docker/container.py enter

# 이제 컨테이너 내부 bash 셸에 들어왔습니다
# 프롬프트가 다음과 같이 변경됨: root@<container-id>:/workspace/isaaclab#
```

##### Step 3: 패키지 설치 (컨테이너 내부)
```bash
# 커스텀 환경 패키지를 Python에 등록 (최초 1회만)
cd /workspace/isaaclab/source/extensions/omni.isaac.lab_tasks
pip install -e .

# 설치 확인
pip list | grep my-environments
# 출력: my-environments    1.0.0    /workspace/isaaclab/source/extensions/omni.isaac.lab_tasks
```

##### Step 4: 환경 테스트 실행 (컨테이너 내부)
```bash
# IsaacLab 루트로 이동
cd /workspace/isaaclab

# 헤드리스 모드로 테스트 (GUI 없음, 빠른 테스트)
./isaaclab.sh -p source/extensions/omni.isaac.lab_tasks/my_environments/test_dual_panda.py \
    --headless --num_envs 1 --test_steps 100

# 카메라 기능 포함 테스트 (env_cfg.py에서 카메라 주석 해제 필요)
./isaaclab.sh -p source/extensions/omni.isaac.lab_tasks/my_environments/test_dual_panda.py \
    --headless --enable_cameras --num_envs 1 --test_steps 100

# GUI 모드로 실행하려면 (호스트에서 X11 설정 필요)
# 1. 호스트 터미널에서: xhost +local:docker
# 2. 컨테이너에서:
./isaaclab.sh -p source/extensions/omni.isaac.lab_tasks/my_environments/test_dual_panda.py \
    --num_envs 1
```

##### Step 5: 컨테이너 종료
```bash
# 컨테이너에서 나가기
exit

# 호스트에서 컨테이너 중지
python3 docker/container.py stop
```

#### 💻 로컬 환경에서 실행

##### 1. 패키지 설치
```bash
cd source/extensions/omni.isaac.lab_tasks
pip install -e .
```

##### 2. 환경 테스트
```bash
# GUI 모드
./isaaclab.sh -p source/extensions/omni.isaac.lab_tasks/my_environments/test_dual_panda.py

# 여러 환경 동시 테스트
./isaaclab.sh -p source/extensions/omni.isaac.lab_tasks/my_environments/test_dual_panda.py --num_envs 4
```

#### 🤖 ROS2 제어

##### 독립 실행 모드
```bash
./isaaclab.sh -p source/extensions/omni.isaac.lab_tasks/my_environments/ros2_control.py --standalone
```

##### ROS2 연동 모드
```bash
# ROS2 환경 설정 후
source /opt/ros/humble/setup.bash
./isaaclab.sh -p source/extensions/omni.isaac.lab_tasks/my_environments/ros2_control.py
```

### 환경 구조

```
dual_panda_manipulation/
├── __init__.py          # 환경 등록
├── env_cfg.py          # 환경 설정 (Scene, MDP)
├── mdp/                # MDP 컴포넌트
│   ├── custom_actions.py    # 커스텀 액션
│   ├── custom_observations.py # 커스텀 관측
│   └── custom_rewards.py    # 커스텀 보상
├── agents/             # RL 에이전트 설정
│   └── rsl_rl_ppo_cfg.py   # PPO 설정
└── config/             # 추가 설정 파일

```

### 주요 기능

1. **듀얼 암 제어**
   - 독립 제어 모드
   - 미러링 제어 모드
   - 동기화 제어 모드

2. **센서 시뮬레이션**
   - RGB 카메라
   - 깊이 카메라
   - 접촉 센서

3. **강화학습 태스크**
   - Pick and Place
   - 협력 조작
   - 정밀 조작

### 커스터마이징

새로운 태스크를 추가하려면:

1. `env_cfg.py`에서 Scene 수정
2. `mdp/` 폴더에 커스텀 함수 추가
3. `__init__.py`에서 새 환경 등록

### 트러블슈팅

#### ❌ Import 에러: "No module named 'my_environments'"
```bash
# 해결: 패키지 설치가 안 되어 있음
cd /workspace/isaaclab/source/extensions/omni.isaac.lab_tasks
pip install -e .

# 그래도 안 되면 재설치
pip uninstall my-environments -y
pip install -e .
```

#### ❌ TypeError: ManagerBasedRLEnv.__init__() missing 'cfg'
```bash
# 원인: IsaacLab 환경은 cfg 파라미터가 필수
# 해결: ManagerBasedRLEnv를 직접 사용
# 올바른 환경 생성 방법:
from isaaclab.envs import ManagerBasedRLEnv
from my_environments.dual_panda_manipulation.env_cfg import DualPandaManipulationEnvCfg

env_cfg = DualPandaManipulationEnvCfg()
env_cfg.scene.num_envs = 16
env_cfg.sim.device = "cuda:0"
env = ManagerBasedRLEnv(cfg=env_cfg)
```

#### ❌ AttributeError: 'ActionTerm' has no attribute 'Config'
```bash
# 원인: IsaacLab API 변경
# 해결: ActionTermCfg를 직접 상속
# 수정 전: class MyActionCfg(ActionTerm.Config):
# 수정 후: class MyActionCfg(ActionTermCfg):
```

#### ❌ RuntimeError: Could not find prim with path
```bash
# 원인: Scene에 정의된 객체가 실제로 생성되지 않음
# 해결: prim_path가 올바른지 확인
# 와일드카드 사용시: "Cube_.*" → 실제 인스턴스가 있어야 함
# 단일 객체 사용: "Cube" → 자동으로 생성됨
```

#### ❌ RuntimeError: A camera was spawned without --enable_cameras
```bash
# 원인: 카메라 센서 사용시 플래그 필요
# 해결 1: 카메라를 주석 처리 (빠른 테스트)
# 해결 2: --enable_cameras 플래그 추가
./isaaclab.sh -p ... --enable_cameras
```

#### ❌ Docker 컨테이너 시작 실패
```bash
# 기존 컨테이너 확인
docker ps -a | grep isaac-lab

# 기존 컨테이너가 있으면 삭제 후 재시작
python3 docker/container.py stop
python3 docker/container.py start

# 포트 충돌시 다른 suffix 사용
python3 docker/container.py start --suffix custom
```

#### ❌ "CUDA out of memory" 에러
```bash
# 해결: 환경 개수 줄이기
./isaaclab.sh -p ... --num_envs 1  # 4 대신 1 사용
```

#### ❌ GUI 모드에서 화면이 안 보임
```bash
# 해결 1: 헤드리스 모드 사용
./isaaclab.sh -p ... --headless

# 해결 2: X11 forwarding 설정 (호스트에서)
xhost +local:docker
# 그 후 컨테이너에서 다시 실행
```

#### ❌ 파일 경로를 찾을 수 없음
```bash
# 해결: 올바른 디렉토리에서 실행
pwd  # 현재 위치 확인
cd /workspace/isaaclab  # IsaacLab 루트로 이동
```