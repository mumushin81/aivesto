#!/usr/bin/env python3
"""
Simple Supabase Query Test
"""

import sys
sys.path.append('.')

from supabase import create_client
from config.settings import SUPABASE_URL, SUPABASE_KEY

print(f"SUPABASE_URL: {SUPABASE_URL}")
print(f"SUPABASE_KEY (first 20 chars): {SUPABASE_KEY[:20]}...")

client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("\n테스트 1: news_raw 테이블 조회")
try:
    result = client.table("news_raw").select("*").limit(5).execute()
    print(f"✓ 성공! {len(result.data)} rows")
    for row in result.data:
        print(f"  - {row.get('title', 'No title')[:60]}")
except Exception as e:
    print(f"✗ 실패: {e}")

print("\n테스트 2: analyzed_news 테이블 조회")
try:
    result = client.table("analyzed_news").select("*").limit(5).execute()
    print(f"✓ 성공! {len(result.data)} rows")
except Exception as e:
    print(f"✗ 실패: {e}")
