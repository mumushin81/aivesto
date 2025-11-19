#!/bin/bash
# Midjourney MCP 빠른 설정 스크립트
# 작성일: 2025-11-15

set -e  # 에러 발생 시 중단

echo "=========================================="
echo "Midjourney MCP 설정 스크립트"
echo "=========================================="
echo ""

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. uvx 설치 확인
echo "1️⃣  uvx 설치 확인 중..."
if command -v uvx &> /dev/null; then
    echo -e "${GREEN}✓ uvx가 이미 설치되어 있습니다${NC}"
else
    echo -e "${YELLOW}⚠️  uvx가 설치되지 않았습니다${NC}"
    echo "   uv를 설치하시겠습니까? (y/n)"
    read -r install_uv

    if [ "$install_uv" = "y" ]; then
        echo "   uv 설치 중..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        echo -e "${GREEN}✓ uv 설치 완료${NC}"
    else
        echo -e "${RED}✗ uvx 없이는 진행할 수 없습니다${NC}"
        echo "   대안: GPTNB API 방식 사용 (docs/MIDJOURNEY_MCP_SETUP.md 참조)"
        exit 1
    fi
fi

echo ""

# 2. Midjourney 토큰 입력
echo "2️⃣  Midjourney Discord 토큰 입력"
echo ""
echo "   Discord 웹 (https://discord.com)에서 DevTools를 열고"
echo "   Application → Cookies → discord.com 에서 다음 값을 복사하세요:"
echo ""
echo -e "${YELLOW}   __Secure-user_token_r${NC}"
echo -n "   TOKEN_R: "
read -r TOKEN_R

echo ""
echo -e "${YELLOW}   __Secure-user_token_i${NC}"
echo -n "   TOKEN_I: "
read -r TOKEN_I

if [ -z "$TOKEN_R" ] || [ -z "$TOKEN_I" ]; then
    echo -e "${RED}✗ 토큰이 입력되지 않았습니다${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 토큰 입력 완료${NC}"
echo ""

# 3. Claude Desktop 설정 파일 경로
CLAUDE_CONFIG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"

echo "3️⃣  Claude Desktop 설정 파일 확인"
echo "   경로: $CLAUDE_CONFIG"

if [ ! -f "$CLAUDE_CONFIG" ]; then
    echo -e "${YELLOW}⚠️  설정 파일이 없습니다. 새로 생성합니다${NC}"
    mkdir -p "$HOME/Library/Application Support/Claude"
    echo '{"mcpServers":{}}' > "$CLAUDE_CONFIG"
fi

# 백업 생성
BACKUP_FILE="${CLAUDE_CONFIG}.backup.$(date +%Y%m%d_%H%M%S)"
cp "$CLAUDE_CONFIG" "$BACKUP_FILE"
echo -e "${GREEN}✓ 백업 생성: $BACKUP_FILE${NC}"
echo ""

# 4. 설정 업데이트
echo "4️⃣  Midjourney MCP 설정 추가 중..."

# Python으로 JSON 수정 (jq 대신)
python3 - <<EOF
import json
import sys

config_file = "$CLAUDE_CONFIG"

# 기존 설정 읽기
try:
    with open(config_file, 'r') as f:
        config = json.load(f)
except:
    config = {"mcpServers": {}}

# mcpServers 키가 없으면 생성
if "mcpServers" not in config:
    config["mcpServers"] = {}

# Midjourney 설정 추가
config["mcpServers"]["midjourney"] = {
    "command": "uvx",
    "args": ["midjourney-mcp"],
    "env": {
        "TOKEN_R": "$TOKEN_R",
        "TOKEN_I": "$TOKEN_I",
        "API_BASE": "midjourney.com",
        "SUFFIX": "--v 6.1"
    }
}

# 파일에 저장
with open(config_file, 'w') as f:
    json.dump(config, f, indent=2)

print("✓ 설정 파일 업데이트 완료")
EOF

echo -e "${GREEN}✓ Midjourney MCP 설정 추가 완료${NC}"
echo ""

# 5. 완료 메시지
echo "=========================================="
echo -e "${GREEN}✅ 설정 완료!${NC}"
echo "=========================================="
echo ""
echo "다음 단계:"
echo "  1. Claude Desktop을 완전히 종료하세요"
echo "  2. Activity Monitor에서 'Claude' 프로세스가 없는지 확인"
echo "  3. Claude Desktop을 다시 실행하세요"
echo "  4. 새 대화에서 테스트:"
echo ""
echo -e "${YELLOW}     'Midjourney로 futuristic datacenter 이미지를 16:9로 생성해줘'${NC}"
echo ""
echo "백업 파일: $BACKUP_FILE"
echo "문제 발생 시 백업으로 복원하세요"
echo ""
echo "상세 가이드: docs/MIDJOURNEY_MCP_SETUP.md"
echo ""
