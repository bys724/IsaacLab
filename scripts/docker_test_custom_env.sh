#!/bin/bash

# Docker 컨테이너 내부에서 커스텀 환경 테스트
# 
# 사용법:
#   ./scripts/docker_test_custom_env.sh

echo "======================================"
echo "Docker 컨테이너에서 커스텀 환경 실행"  
echo "======================================"

# 컨테이너 이름
CONTAINER_NAME="isaac-sim"

# 컨테이너가 실행 중인지 확인
if [ ! "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
    echo "Docker 컨테이너 시작 중..."
    docker compose -f docker/docker-compose.yaml up -d
    sleep 5
fi

echo ""
echo "커스텀 환경 테스트 실행..."
echo ""

# Docker 컨테이너에서 테스트 실행
docker exec -it $CONTAINER_NAME bash -c "
    cd /workspace/isaaclab
    ./isaaclab.sh -p source/extensions/omni.isaac.lab_tasks/my_environments/test_dual_panda.py \
        --headless \
        --num_envs 1 \
        --test_steps 100
"

echo ""
echo "테스트 완료!"
echo ""
echo "GUI 모드로 실행하려면 컨테이너에 접속하여 다음 명령을 실행하세요:"
echo "  docker exec -it isaac-sim bash"
echo "  ./isaaclab.sh -p source/extensions/omni.isaac.lab_tasks/my_environments/test_dual_panda.py"