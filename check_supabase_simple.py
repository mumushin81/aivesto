#!/usr/bin/env python3
"""
Supabase REST API를 직접 사용하여 데이터베이스 확인
"""
import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def check_table(table_name, description):
    """REST API로 테이블 데이터 확인"""
    print(f"\n{'='*80}")
    print(f"📊 {description} ({table_name})")
    print(f"{'='*80}")

    url = f"{SUPABASE_URL}/rest/v1/{table_name}?select=*&limit=1000"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            count = len(data)

            if count == 0:
                print("❌ 데이터 없음")
                return 0

            print(f"✅ 총 {count}개 데이터 발견\n")

            # 처음 5개 항목 출력
            for i, item in enumerate(data[:5], 1):
                print(f"--- [{i}] ---")
                for key, value in item.items():
                    if isinstance(value, str) and len(value) > 100:
                        print(f"  {key}: {value[:100]}...")
                    elif isinstance(value, list):
                        print(f"  {key}: {value}")
                    else:
                        print(f"  {key}: {value}")
                print()

            if count > 5:
                print(f"... 외 {count - 5}개 항목 더 있음\n")

            return count
        else:
            print(f"❌ 오류: HTTP {response.status_code}")
            print(f"   응답: {response.text}")
            return 0

    except Exception as e:
        print(f"❌ 오류: {e}")
        return 0

def main():
    print("\n" + "="*80)
    print("🔍 SUPABASE 데이터베이스 상태 확인 (REST API)")
    print("="*80)

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ 환경 변수가 설정되지 않았습니다.")
        print("   .env 파일에 SUPABASE_URL과 SUPABASE_KEY를 설정하세요.")
        return

    print(f"✅ Supabase URL: {SUPABASE_URL}")
    print(f"✅ API Key 설정됨 (길이: {len(SUPABASE_KEY)})")

    # 각 테이블 확인
    tables = {
        "news_raw": "원본 뉴스 데이터 (24시간 TTL)",
        "analyzed_news": "분석된 뉴스 (투자 신호)",
        "published_articles": "발행된 블로그 기사",
        "articles": "다층 수집 시스템 (Layer 1/2/3)",
        "signals": "투자 신호 테이블"
    }

    summary = {}
    for table_name, description in tables.items():
        count = check_table(table_name, description)
        summary[table_name] = count

    # 최종 요약
    print("\n" + "="*80)
    print("📈 데이터베이스 요약")
    print("="*80)
    total = 0
    for table_name, count in summary.items():
        status = "✅" if count > 0 else "❌"
        print(f"{status} {table_name}: {count}개")
        total += count

    print(f"\n📊 전체 레코드 수: {total}개")
    print("\n" + "="*80)
    print(f"⏰ 확인 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")

if __name__ == '__main__':
    main()
