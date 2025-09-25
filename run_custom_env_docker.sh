#!/bin/bash

# 커스텀 환경 Docker 실행 스크립트
# IsaacLab의 공식 Docker 컨테이너를 사용하여 커스텀 환경 실행

set -e  # 에러 발생시 중단

echo "================================================"
echo "   IsaacLab 커스텀 환경 Docker 실행 스크립트"
echo "================================================"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 프로젝트 루트 확인
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# 명령 인자 파싱
COMMAND=${1:-test}
HEADLESS=${2:-}

# 함수: 컨테이너 상태 확인
check_container() {
    if docker ps -q -f name=isaac-lab-base > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# 함수: 에러 메시지 출력
error_exit() {
    echo -e "${RED}❌ 에러: $1${NC}" >&2
    exit 1
}

# 함수: 성공 메시지 출력
success_msg() {
    echo -e "${GREEN}✓ $1${NC}"
}

# 함수: 정보 메시지 출력
info_msg() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

case "$COMMAND" in
    start)
        info_msg "Docker 컨테이너 시작 중..."
        python3 docker/container.py start base || error_exit "컨테이너 시작 실패"
        success_msg "컨테이너 시작 완료"
        
        info_msg "패키지 설치 중..."
        docker exec isaac-lab-base bash -c "
            cd /workspace/isaaclab/source/extensions/omni.isaac.lab_tasks
            pip install -e . > /dev/null 2>&1
        " || error_exit "패키지 설치 실패"
        success_msg "패키지 설치 완료"
        ;;
        
    test)
        if ! check_container; then
            info_msg "컨테이너가 실행중이지 않습니다. 시작합니다..."
            $0 start
        fi
        
        info_msg "테스트 실행 중..."
        
        if [ "$HEADLESS" == "headless" ]; then
            info_msg "헤드리스 모드로 실행합니다"
            docker exec -it isaac-lab-base bash -c "
                cd /workspace/isaaclab
                ./isaaclab.sh -p source/extensions/omni.isaac.lab_tasks/my_environments/test_dual_panda.py \
                    --headless --num_envs 1 --test_steps 100
            "
        else
            info_msg "GUI 모드로 실행합니다 (X11 forwarding 필요)"
            # X11 권한 설정
            xhost +local:docker 2>/dev/null || true
            
            docker exec -it isaac-lab-base bash -c "
                cd /workspace/isaaclab
                ./isaaclab.sh -p source/extensions/omni.isaac.lab_tasks/my_environments/test_dual_panda.py \
                    --num_envs 1 --test_steps 100
            "
        fi
        success_msg "테스트 완료"
        ;;
        
    enter)
        if ! check_container; then
            error_exit "컨테이너가 실행중이지 않습니다. 먼저 './run_custom_env_docker.sh start'를 실행하세요"
        fi
        
        info_msg "컨테이너에 접속합니다..."
        python3 docker/container.py enter
        ;;
        
    stop)
        info_msg "컨테이너 중지 중..."
        python3 docker/container.py stop || error_exit "컨테이너 중지 실패"
        success_msg "컨테이너 중지 완료"
        ;;
        
    status)
        if check_container; then
            success_msg "컨테이너가 실행 중입니다"
            docker ps -f name=isaac-lab-base --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        else
            info_msg "컨테이너가 실행중이지 않습니다"
        fi
        ;;
        
    help|*)
        echo "사용법: $0 [명령] [옵션]"
        echo ""
        echo "명령:"
        echo "  start           - Docker 컨테이너 시작 및 패키지 설치"
        echo "  test [headless] - 커스텀 환경 테스트 실행"
        echo "  enter          - 컨테이너 bash 셸 접속"
        echo "  stop           - 컨테이너 중지"
        echo "  status         - 컨테이너 상태 확인"
        echo "  help           - 도움말 표시"
        echo ""
        echo "예시:"
        echo "  $0 start            # 컨테이너 시작"
        echo "  $0 test             # GUI 모드로 테스트"
        echo "  $0 test headless    # 헤드리스 모드로 테스트"
        echo "  $0 enter            # 컨테이너 접속"
        echo "  $0 stop             # 컨테이너 중지"
        ;;
esac

echo ""
echo "================================================"