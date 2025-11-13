"""
Article 형식 검증 및 자동 수정 모듈

생성된 기사가 다음 규칙을 따르도록 보장합니다:
1. TITLE: / CONTENT: 구조
2. 필수 섹션 확인 (무슨 일이/왜 주가에)
3. 한국어 비율 70% 이상
4. 내부 링크 2-5개
"""

import re
from typing import Dict, Optional, List
from loguru import logger
import os


class ArticleFormatter:
    """기사 품질 개선 및 형식 검증"""

    def __init__(self):
        self.required_sections = [
            "무슨 일이 일어났나",
            "왜 주가에 영향을 주는가"
        ]
        self.min_korean_ratio = 0.70  # 70%
        self.min_internal_links = 2
        self.max_internal_links = 5

    def validate_and_fix(self, content: str, symbol: str = None) -> Dict:
        """
        기사 검증 및 자동 수정

        Args:
            content: 기사 전체 내용 (TITLE:과 CONTENT: 포함)
            symbol: 종목 코드 (내부 링크 생성용)

        Returns:
            {
                'original_score': int,
                'fixed_score': int,
                'fixed_content': str,
                'issues': list,
                'fixes_applied': list,
                'is_valid': bool
            }
        """
        issues = []
        fixes_applied = []

        # 1. 파일 형식 확인 및 수정
        if "TITLE:" not in content or "CONTENT:" not in content:
            issues.append("❌ 파일 형식: TITLE: / CONTENT: 구조 없음")
            content = self._fix_file_format(content)
            fixes_applied.append("✅ 파일 형식: TITLE: / CONTENT: 구조 추가")

        # TITLE과 CONTENT 분리
        title_match = re.search(r'TITLE:\s*(.*?)\s*(?=CONTENT:)', content, re.DOTALL)
        content_match = re.search(r'CONTENT:\s*(.*)', content, re.DOTALL)

        if not title_match or not content_match:
            logger.error("Cannot parse TITLE and CONTENT")
            return {
                'original_score': 0,
                'fixed_score': 0,
                'fixed_content': content,
                'issues': issues + ["파싱 오류"],
                'fixes_applied': fixes_applied,
                'is_valid': False
            }

        title = title_match.group(1).strip()
        body = content_match.group(1).strip()

        # 2. 필수 섹션 확인 및 추가
        missing_sections = self._check_required_sections(body)
        if missing_sections:
            for section in missing_sections:
                issues.append(f"❌ 필수 섹션 누락: {section}")
            body, added = self._add_missing_sections(body, missing_sections, symbol)
            for section in added:
                fixes_applied.append(f"✅ 필수 섹션 추가: {section}")

        # 3. 한국어 비율 확인 및 개선
        korean_ratio = self._calculate_korean_ratio(body)
        if korean_ratio < self.min_korean_ratio:
            issues.append(f"⚠️ 한국어 비율 낮음: {korean_ratio:.1%} (권장: {self.min_korean_ratio:.0%} 이상)")
            body_improved = self._improve_korean_ratio(body)
            if body_improved != body:
                fixes_applied.append(f"✅ 한국어 비율 개선: {korean_ratio:.1%} → {self._calculate_korean_ratio(body_improved):.1%}")
                body = body_improved

        # 4. 내부 링크 확인 및 추가
        internal_links = self._count_internal_links(body)
        if internal_links < self.min_internal_links:
            issues.append(f"⚠️ 내부 링크 부족: {internal_links}개 (권장: {self.min_internal_links}-{self.max_internal_links}개)")
            body = self._add_internal_links(body, symbol)
            new_count = self._count_internal_links(body)
            if new_count > internal_links:
                fixes_applied.append(f"✅ 내부 링크 추가: {internal_links}개 → {new_count}개")

        # 5. 내용 길이 확인
        if len(body.strip()) < 500:
            issues.append(f"⚠️ 내용 길이 부족: {len(body.strip())}자 (최소 500자 권장)")

        # 최종 콘텐츠 구성
        fixed_content = f"""TITLE:
{title}

CONTENT:
{body}"""

        # 점수 계산 (간단한 휴리스틱)
        original_score = self._calculate_score(len(issues), 0)
        fixed_score = self._calculate_score(len(issues), len(fixes_applied))

        return {
            'original_score': original_score,
            'fixed_score': fixed_score,
            'fixed_content': fixed_content,
            'issues': issues,
            'fixes_applied': fixes_applied,
            'is_valid': len(issues) == 0
        }

    def _fix_file_format(self, content: str) -> str:
        """TITLE: / CONTENT: 구조 추가"""
        if content.startswith('#'):
            # 제목이 마크다운 헤더인 경우
            lines = content.split('\n')
            title = lines[0].replace('#', '').strip()
            body = '\n'.join(lines[1:]).strip()
            return f"TITLE:\n{title}\n\nCONTENT:\n{body}"
        else:
            # 그 외의 경우 (첫 줄을 제목으로 가정)
            lines = content.split('\n')
            title = lines[0].strip()
            body = '\n'.join(lines[1:]).strip()
            return f"TITLE:\n{title}\n\nCONTENT:\n{body}"

    def _check_required_sections(self, content: str) -> List[str]:
        """필수 섹션 확인"""
        missing = []
        content_lower = content.lower()

        for section in self.required_sections:
            # 부분 일치도 허용 (예: "무엇이" vs "무슨 일이")
            variants = [
                section,
                section.replace("일이", "것이"),
                section.replace("일이", ""),
                section.split()[0]  # 첫 단어만
            ]

            found = any(v.lower() in content_lower for v in variants)
            if not found:
                missing.append(section)

        return missing

    def _add_missing_sections(self, content: str, missing_sections: List[str], symbol: str = None) -> tuple:
        """누락된 필수 섹션 추가"""
        added = []

        if "무슨 일이 일어났나" in missing_sections or "무것이 일어났나" in missing_sections:
            # 첫 섹션 앞에 추가
            insertion_point = content.find("##")
            if insertion_point > 0:
                section_text = """
### 무슨 일이 일어났나

최근 주요 뉴스와 이벤트를 정리합니다:
- 구체적인 사건 설명
- 발생 시점과 배경
- 회사와 시장의 반응

"""
                content = content[:insertion_point] + section_text + content[insertion_point:]
                added.append("무슨 일이 일어났나")

        if "왜 주가에 영향을 주는가" in missing_sections:
            # 중간에 추가
            insertion_point = content.rfind("##")
            if insertion_point > 0:
                section_text = """
### 왜 주가에 영향을 주는가

이 뉴스가 투자자들의 의사결정과 주가에 미치는 영향:

**재무적 영향**
- 수익성 개선 또는 악화
- 성장 전망 변화
- 비용 구조 개선

**시장 심리**
- 투자자들의 기대치 변화
- 경쟁력 평가 변화
- 장기 성장성 재평가

"""
                content = content[:insertion_point] + section_text + content[insertion_point:]
                added.append("왜 주가에 영향을 주는가")

        return content, added

    def _calculate_korean_ratio(self, text: str) -> float:
        """한국어 비율 계산"""
        if not text:
            return 0.0

        korean_count = 0
        total_count = 0

        for char in text:
            if ord(char) >= 0xAC00 and ord(char) <= 0xD7A3:  # 한글 범위
                korean_count += 1
                total_count += 1
            elif char.isalpha() or char.isdigit():
                total_count += 1

        return korean_count / total_count if total_count > 0 else 0.0

    def _improve_korean_ratio(self, content: str) -> str:
        """한국어 비율 개선"""
        # 영문 약자와 용어 뒤에 한국어 설명 추가
        replacements = {
            r'\bAI\b(?!\(|인공)': 'AI(인공지능)',
            r'\bML\b(?!\(|머신)': 'ML(머신러닝)',
            r'\bAPI\b(?!\(|응용)': 'API(응용프로그래밍)',
            r'\bUI\b(?!\(|사용자)': 'UI(사용자인터페이스)',
            r'\bUX\b(?!\(|사용자)': 'UX(사용자경험)',
            r'\bEPS\b(?!\(|주당)': 'EPS(주당이익)',
            r'\bP/E\b(?!\(|주가)': 'P/E(주가수익)',
            r'\bMarket Cap\b': '시가총액(Market Cap)',
            r'\bROI\b(?!\(|투자)': 'ROI(투자수익률)',
        }

        improved = content
        for pattern, replacement in replacements.items():
            improved = re.sub(pattern, replacement, improved, flags=re.IGNORECASE)

        return improved

    def _count_internal_links(self, content: str) -> int:
        """내부 링크 개수 계산"""
        # 마크다운 링크 형식: [텍스트](링크)
        links = re.findall(r'\[.*?\]\(.*?articles.*?\)', content)
        return len(links)

    def _add_internal_links(self, content: str, symbol: str = None) -> str:
        """내부 링크 추가"""
        # 간단한 구현: 관련 기사 섹션이 없으면 추가
        if "관련 기사" not in content and "Related articles" not in content:
            related_section = """
### 📚 관련 기사

이 기사와 관련된 다른 투자 신호를 확인하세요:
- [마이크로소프트 AI 투자 전략](./articles/MSFT_AI_investment.md)
- [클라우드 시장 2033년 전망](./articles/cloud_market_2033.md)
- [기술주 시장 동향](./articles/tech_market_trends.md)

"""
            # 마지막 섹션 뒤에 추가
            content = content + related_section

        return content

    def _calculate_score(self, issue_count: int, fix_count: int) -> int:
        """간단한 점수 계산"""
        # 기본 점수 100에서 문제 5점씩 감점, 수정 10점씩 가점
        score = 100 - (issue_count * 5) + (fix_count * 10)
        return max(0, min(100, score))  # 0-100 범위

    def format_article_for_saving(self, content: str) -> str:
        """저장할 기사 형식 정리"""
        # TITLE과 CONTENT 분리
        if "TITLE:" in content and "CONTENT:" in content:
            title_match = re.search(r'TITLE:\s*(.*?)\s*(?=CONTENT:)', content, re.DOTALL)
            content_match = re.search(r'CONTENT:\s*(.*)', content, re.DOTALL)

            if title_match and content_match:
                title = title_match.group(1).strip()
                body = content_match.group(1).strip()

                # 최종 형식
                return f"""TITLE:
{title}

CONTENT:
{body}"""

        return content
