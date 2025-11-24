#!/bin/bash
# Supabase 데이터베이스 스키마 자동 설정 스크립트

echo "================================================================================"
echo "🔧 Supabase 데이터베이스 스키마 설정"
echo "================================================================================"
echo ""
echo "스키마를 생성하는 방법을 선택하세요:"
echo ""
echo "방법 1: Supabase Dashboard 사용 (권장)"
echo "  1. https://supabase.com/dashboard 로그인"
echo "  2. 프로젝트 선택 (czubqsnahmtdsmnyawlk)"
echo "  3. 좌측 메뉴 → SQL Editor"
echo "  4. database/schema.sql 내용 복사 & 붙여넣기"
echo "  5. Run 버튼 클릭"
echo ""
echo "방법 2: PostgreSQL 직접 연결 (Database password 필요)"
echo "  - Supabase Dashboard → Settings → Database에서 password 확인 필요"
echo ""
echo "================================================================================"
echo ""

read -p "Database password가 있으신가요? (y/n): " has_password

if [ "$has_password" = "y" ] || [ "$has_password" = "Y" ]; then
    echo ""
    read -sp "Database password를 입력하세요: " db_password
    echo ""

    PROJECT_REF="czubqsnahmtdsmnyawlk"
    DB_HOST="db.${PROJECT_REF}.supabase.co"

    echo ""
    echo "🔌 PostgreSQL 연결 시도 중..."
    echo "Host: $DB_HOST"

    # psql 설치 확인
    if ! command -v psql &> /dev/null; then
        echo "❌ psql이 설치되지 않았습니다."
        echo "설치: apt-get install postgresql-client"
        exit 1
    fi

    # 스키마 실행
    PGPASSWORD="$db_password" psql -h "$DB_HOST" -p 5432 -U postgres -d postgres -f database/schema.sql

    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ 스키마 생성 완료!"
    else
        echo ""
        echo "❌ 스키마 생성 실패"
        echo "Supabase Dashboard에서 수동으로 실행해주세요."
    fi
else
    echo ""
    echo "📋 다음 단계:"
    echo "1. 아래 URL을 열어주세요:"
    echo "   https://supabase.com/dashboard/project/czubqsnahmtdsmnyawlk/sql"
    echo ""
    echo "2. 다음 파일의 내용을 복사하여 붙여넣으세요:"
    echo "   database/schema.sql"
    echo ""
    echo "3. Run 버튼을 클릭하세요."
    echo ""

    # schema.sql 표시
    echo "================================================================================"
    echo "📄 database/schema.sql 내용:"
    echo "================================================================================"
    cat database/schema.sql
fi
