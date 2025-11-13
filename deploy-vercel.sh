#!/bin/bash

# Aivesto Dashboard Vercel 배포 스크립트
# Usage: bash deploy-vercel.sh

set -e

echo "🚀 Aivesto Dashboard Vercel 배포 시작"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1. Vercel CLI 확인
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI가 설치되지 않았습니다."
    echo "다음 명령어로 설치하세요:"
    echo "  npm install -g vercel"
    exit 1
fi

echo "✅ Vercel CLI 확인"

# 2. 프로젝트 상태 확인
if [ ! -f "vercel.json" ]; then
    echo "❌ vercel.json 파일이 없습니다."
    exit 1
fi

if [ ! -d "public" ]; then
    echo "❌ public 디렉토리가 없습니다."
    exit 1
fi

echo "✅ 프로젝트 파일 확인"

# 3. 환경변수 확인
if [ ! -f ".env" ]; then
    echo "⚠️  .env 파일이 없습니다. .env.example을 복사합니다."
    cp .env.example .env
    echo "👉 .env 파일을 수정하고 다시 실행하세요."
    exit 1
fi

echo "✅ 환경변수 확인"

# 4. Git 상태 확인
if [ -z "$(git status --porcelain)" ]; then
    echo "✅ Working directory clean"
else
    echo "⚠️  Working directory에 변경사항이 있습니다."
    echo "변경사항을 커밋하려면 y를 입력하세요."
    read -p "커밋하시겠습니까? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add -A
        git commit -m "Pre-deploy commit"
    fi
fi

# 5. Vercel 배포
echo ""
echo "📤 Vercel에 배포 중..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 첫 번째 배포 (프리뷰)
read -p "프리뷰로 배포하시겠습니까? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    vercel
else
    echo "프리뷰 배포를 건너뜁니다."
fi

# 프로덕션 배포
echo ""
read -p "프로덕션에 배포하시겠습니까? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    vercel --prod
    echo ""
    echo "✅ 프로덕션 배포 완료!"
    echo ""
    echo "다음 단계:"
    echo "1. 대시보드 URL을 방문하여 확인하세요."
    echo "2. Vercel 환경변수를 설정하세요:"
    echo "   - TELEGRAM_BOT_TOKEN"
    echo "   - TELEGRAM_CHAT_IDS"
    echo "3. API 서버 URL을 public/index.html의 API_BASE에 설정하세요."
else
    echo "프로덕션 배포를 건너뜁니다."
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 배포 스크립트 완료"
