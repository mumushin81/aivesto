#!/usr/bin/env python3
"""
Supabase 데이터베이스 내용 확인 스크립트
모든 테이블의 데이터를 조회하고 리스트로 정리
"""
import sys
from database.supabase_client import SupabaseClient
from datetime import datetime
import json

def check_table_data(db_client, table_name, description):
    """테이블 데이터 확인"""
    print(f"\n{'='*80}")
    print(f"📊 {description} ({table_name})")
    print(f"{'='*80}")

    try:
        # 전체 데이터 조회
        result = db_client.client.table(table_name).select("*").limit(1000).execute()

        if not result.data:
            print("❌ 데이터 없음")
            return 0

        count = len(result.data)
        print(f"✅ 총 {count}개 데이터 발견\n")

        # 처음 5개 항목 상세 출력
        for i, item in enumerate(result.data[:5], 1):
            print(f"--- [{i}] ---")
            for key, value in item.items():
                # 긴 텍스트는 요약
                if isinstance(value, str) and len(value) > 100:
                    print(f"  {key}: {value[:100]}...")
                elif isinstance(value, list) and len(value) > 0:
                    print(f"  {key}: {value}")
                else:
                    print(f"  {key}: {value}")
            print()

        if count > 5:
            print(f"... 외 {count - 5}개 항목 더 있음\n")

        return count

    except Exception as e:
        print(f"❌ 오류: {e}")
        return 0

def main():
    print("\n" + "="*80)
    print("🔍 SUPABASE 데이터베이스 상태 확인")
    print("="*80)

    # Supabase 연결
    try:
        db = SupabaseClient()
        print("✅ Supabase 연결 성공")
    except Exception as e:
        print(f"❌ Supabase 연결 실패: {e}")
        sys.exit(1)

    # 각 테이블 확인
    tables_info = {
        "news_raw": "원본 뉴스 데이터 (24시간 TTL)",
        "analyzed_news": "분석된 뉴스 (투자 신호)",
        "published_articles": "발행된 블로그 기사",
        "articles": "다층 수집 시스템 (Layer 1/2/3)",
        "signals": "투자 신호 테이블"
    }

    summary = {}

    for table_name, description in tables_info.items():
        count = check_table_data(db, table_name, description)
        summary[table_name] = count

    # 최종 요약
    print("\n" + "="*80)
    print("📈 데이터베이스 요약")
    print("="*80)
    for table_name, count in summary.items():
        status = "✅" if count > 0 else "❌"
        print(f"{status} {table_name}: {count}개")

    print("\n" + "="*80)
    print(f"⏰ 확인 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")

if __name__ == '__main__':
    main()
