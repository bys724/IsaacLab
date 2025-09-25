#!/bin/bash

# 커스텀 환경 테스트 스크립트
# 
# 사용법:
#   ./scripts/test_custom_env.sh          # GUI 모드로 테스트
#   ./scripts/test_custom_env.sh headless # 헤드리스 모드로 테스트

echo "======================================"
echo "듀얼 Panda 커스텀 환경 테스트"
echo "======================================"

# 스크립트 위치에서 프로젝트 루트 디렉토리 찾기
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 프로젝트 루트로 이동
cd "$PROJECT_ROOT"

# 헤드리스 옵션 확인
HEADLESS_FLAG=""
if [ "$1" == "headless" ]; then
    HEADLESS_FLAG="--headless"
    echo "헤드리스 모드로 실행합니다..."
else
    echo "GUI 모드로 실행합니다..."
fi

# 환경 테스트 실행
echo ""
echo "테스트 실행 중..."
./isaaclab.sh -p source/extensions/omni.isaac.lab_tasks/my_environments/test_dual_panda.py \
    --num_envs 1 \
    --test_steps 500 \
    $HEADLESS_FLAG

echo ""
echo "테스트 완료!"