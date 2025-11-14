#!/usr/bin/env python3
"""
articles 폴더의 파일들을 SEO 마크다운 형식으로 변환하는 스크립트
TITLE/CONTENT 형식 → 순수 마크다운 형식 변환
"""

import re
import os
from pathlib import Path

ARTICLES_DIR = Path(__file__).parent.parent / 'articles'

def convert_file_to_markdown(file_path):
    """파일을 SEO 마크다운 형식으로 변환"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # TITLE: 형식 감지
    title_match = re.search(r'^TITLE:\n(.+?)(?:\n\n|\nCONTENT:)', content, re.MULTILINE)
    if not title_match:
        print(f"⚠️  {file_path.name}: TITLE 형식을 찾을 수 없습니다")
        return False

    title = title_match.group(1).strip()

    # CONTENT: 이후의 내용 추출
    content_match = re.search(r'^CONTENT:\n(.+)$', content, re.MULTILINE | re.DOTALL)
    if not content_match:
        print(f"⚠️  {file_path.name}: CONTENT 형식을 찾을 수 없습니다")
        return False

    body_content = content_match.group(1).strip()

    # 새로운 형식으로 변환
    markdown_content = f"# {title}\n\n{body_content}"

    # 파일에 저장
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    print(f"✅ {file_path.name}: 변환 완료")
    return True

def main():
    """모든 article_*.md 파일 변환"""
    article_files = sorted(ARTICLES_DIR.glob('article_*.md'))

    if not article_files:
        print(f"❌ articles 폴더에 파일이 없습니다: {ARTICLES_DIR}")
        return

    print(f"\n📝 {len(article_files)}개 파일 변환 시작\n")
    print("=" * 60)

    converted = 0
    skipped = 0

    for file_path in article_files:
        # 이미 마크다운 형식인지 확인
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()

        if first_line.startswith('# '):
            print(f"⏭️  {file_path.name}: 이미 마크다운 형식 (스킵)")
            skipped += 1
        elif 'TITLE:' in first_line or file_path.read_text(encoding='utf-8').startswith('TITLE:'):
            if convert_file_to_markdown(file_path):
                converted += 1
        else:
            print(f"❓ {file_path.name}: 알 수 없는 형식")
            skipped += 1

    print("=" * 60)
    print(f"\n📊 변환 결과:")
    print(f"  ✅ 변환 완료: {converted}개")
    print(f"  ⏭️  스킵됨: {skipped}개")
    print(f"  📝 총 파일: {len(article_files)}개\n")

if __name__ == '__main__':
    main()
