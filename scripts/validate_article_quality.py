"""
블로그 기사 품질 검사 스크립트
Article Quality Validation Script

11단계 구조 및 SEO 규칙 검증
"""

import re
import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
from loguru import logger

sys.path.append('..')


class ArticleValidator:
    """블로그 기사 품질 검사 클래스"""

    # 11단계 필수 구조
    REQUIRED_SECTIONS = [
        ("제목", "title"),  # 1. 제목 (60자 이내)
        ("핵심 요약", "summary"),  # 2. 10초 요약
        ("무슨 일이 일어났나", "what_happened"),  # 3. What happened
        ("어떻게 작동하나", "how_it_works"),  # 4. How it works
        ("왜 주가에 영향을 주나", "why_impact"),  # 5. Why it impacts
        ("숫자 분석", "numbers"),  # 6. Numbers
        ("경쟁사 비교", "competitor"),  # 7. Competitor comparison
        ("FAQ", "faq"),  # 8. FAQ
        ("전문가 의견", "expert"),  # 9. Expert opinions
        ("단계별 예측", "forecast"),  # 10. Phased forecast
        ("결론", "conclusion")  # 11. Conclusion
    ]

    # SEO 규칙
    SEO_RULES = {
        "title_length": (20, 60),  # 제목 길이: 20-60자
        "min_keywords": 3,  # 최소 키워드 수
        "keyword_density": (1, 3),  # 키워드 밀도: 1-3%
        "heading_count": (5, 20),  # 헤딩 수: 5-20개
        "paragraph_length": (50, 300),  # 문단 길이: 50-300자
        "internal_links": (2, 10),  # 내부 링크: 2-10개
        "meta_description": (120, 160),  # 메타 설명: 120-160자
        "readability_score": 60,  # 가독성 점수: 60 이상
    }

    def __init__(self):
        """초기화"""
        self.validation_results = {}
        self.errors = []
        self.warnings = []
        self.suggestions = []

    def validate_article(self, file_path: str) -> Dict:
        """
        기사 파일 검증

        Args:
            file_path: 기사 파일 경로

        Returns:
            검증 결과 딕셔너리
        """
        self.errors = []
        self.warnings = []
        self.suggestions = []

        if not Path(file_path).exists():
            logger.error(f"File not found: {file_path}")
            return {"status": "error", "message": f"파일을 찾을 수 없음: {file_path}"}

        # 파일 읽기
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Failed to read file: {e}")
            return {"status": "error", "message": f"파일 읽기 실패: {e}"}

        # 기본 검증
        self._validate_file_format(content)
        self._validate_structure(content)
        self._validate_seo(content)
        self._validate_writing_rules(content)

        # 결과 종합
        total_checks = 11  # 11단계
        passed_sections = self._count_sections(content)

        result = {
            "status": "success" if not self.errors else "warning",
            "file": Path(file_path).name,
            "timestamp": datetime.now().isoformat(),
            "sections_passed": passed_sections,
            "total_sections": total_checks,
            "completion_rate": f"{int((passed_sections / total_checks) * 100)}%",
            "errors": self.errors,
            "warnings": self.warnings,
            "suggestions": self.suggestions,
            "score": self._calculate_score()
        }

        return result

    def _validate_file_format(self, content: str):
        """파일 형식 검증"""
        # TITLE과 CONTENT 구분 확인
        if "TITLE:" not in content or "CONTENT:" not in content:
            self.errors.append("❌ 파일 형식: TITLE: / CONTENT: 구조 없음")
        else:
            self.suggestions.append("✅ 기본 파일 형식 준수")

        # 기본 내용 길이
        content_section = content.split("CONTENT:")[-1].strip() if "CONTENT:" in content else ""
        if len(content_section) < 500:
            self.errors.append(f"❌ 내용 길이 부족: {len(content_section)}자 (최소 500자 권장)")
        elif len(content_section) < 1000:
            self.warnings.append(f"⚠️ 내용 길이 부족: {len(content_section)}자 (권장: 1000-3000자)")

    def _validate_structure(self, content: str):
        """11단계 구조 검증"""
        content_lower = content.lower()
        section_mapping = {
            "무슨 일이 일어났나": ["무슨 일이 일어났나", "what happened", "뉴스 내용", "사건"],
            "어떻게 작동하나": ["어떻게 작동하나", "how it works", "비즈니스 로직", "작동 방식"],
            "왜 주가에 영향을 주나": ["왜 주가에 영향", "why it impacts", "주가 영향", "투자 관점"],
            "숫자 분석": ["숫자", "수치", "통계", "데이터", "numbers", "figure"],
            "경쟁사 비교": ["경쟁사", "경쟁", "비교", "competitor", "comparison"],
            "FAQ": ["faq", "자주 묻는 질문", "질문과 답변", "q&a"],
            "전문가 의견": ["전문가", "애널리스트", "의견", "평가", "expert", "analyst"],
            "단계별 예측": ["예측", "전망", "시나리오", "단기", "중기", "장기", "forecast"],
            "결론": ["결론", "종합", "정리", "요약", "conclusion", "summary"]
        }

        found_sections = {}
        for section_name, keywords in section_mapping.items():
            for keyword in keywords:
                if keyword in content_lower:
                    found_sections[section_name] = True
                    break

        # 필수 섹션 확인
        essential_sections = ["무슨 일이 일어났나", "왜 주가에 영향을 주나", "결론"]
        missing_sections = [s for s in essential_sections if s not in found_sections]

        if missing_sections:
            for section in missing_sections:
                self.errors.append(f"❌ 필수 섹션 누락: {section}")

        for section_name in found_sections:
            self.suggestions.append(f"✅ 구조 확인: {section_name} 포함")

        # 헤딩 개수 확인
        headings = re.findall(r'^#{1,3}\s+.+$', content, re.MULTILINE)
        if len(headings) < 3:
            self.warnings.append(f"⚠️ 헤딩 부족: {len(headings)}개 (권장: 5개 이상)")
        else:
            self.suggestions.append(f"✅ 구조 헤딩: {len(headings)}개 사용")

    def _validate_seo(self, content: str):
        """SEO 규칙 검증"""
        # 제목 길이 확인
        title_match = re.search(r'TITLE:\s*\n?(.+?)(?:\n|$)', content)
        if title_match:
            title = title_match.group(1).strip()
            title_length = len(title)
            if title_length < 20:
                self.errors.append(f"❌ SEO 제목 길이 짧음: {title_length}자 (권장: 20-60자)")
            elif title_length > 60:
                self.errors.append(f"❌ SEO 제목 길이 김: {title_length}자 (권장: 20-60자)")
            else:
                self.suggestions.append(f"✅ SEO 제목: {title_length}자 (최적)")

            # 키워드 확인 (종목명, 핵심 용어)
            keywords = self._extract_keywords(title)
            if len(keywords) >= 2:
                self.suggestions.append(f"✅ 제목 키워드: {len(keywords)}개 포함")
            else:
                self.warnings.append(f"⚠️ 제목 키워드 부족: {len(keywords)}개 (권장: 2개 이상)")

        # 문단 길이 확인
        paragraphs = re.split(r'\n\n+', content)
        short_paragraphs = [p for p in paragraphs if len(p) < 50 and len(p) > 5]
        if short_paragraphs:
            self.warnings.append(f"⚠️ 짧은 문단: {len(short_paragraphs)}개 (권장: 50자 이상)")

        # 숫자 사용 확인
        numbers = re.findall(r'\d+(?:%|년|월|일|B|M|K|$)?', content)
        if len(numbers) >= 5:
            self.suggestions.append(f"✅ 숫자 활용: {len(numbers)}개 통계/수치 포함")
        else:
            self.warnings.append(f"⚠️ 숫자 부족: {len(numbers)}개 (권장: 5개 이상)")

        # 내부 링크 확인
        links = re.findall(r'\[.+?\]\(.+?\)', content)
        if len(links) >= 2:
            self.suggestions.append(f"✅ 내부 링크: {len(links)}개 포함")
        elif len(links) == 0:
            self.warnings.append(f"⚠️ 링크 없음 (권장: 2-5개 내부 링크)")

    def _validate_writing_rules(self, content: str):
        """글쓰기 문서화 규칙 검증"""
        issues = []

        # 1. 한국어/영어 혼용 검증
        korean_ratio = self._calculate_korean_ratio(content)
        if korean_ratio < 70:
            self.warnings.append(f"⚠️ 한국어 비율 낮음: {korean_ratio:.1f}% (권장: 70% 이상)")
        else:
            self.suggestions.append(f"✅ 한국어 비율: {korean_ratio:.1f}%")

        # 2. 문장 길이 검증
        sentences = re.split(r'[.!?]\s+', content)
        long_sentences = [s for s in sentences if len(s) > 100]
        if len(long_sentences) > len(sentences) * 0.3:  # 30% 이상 길면 경고
            self.warnings.append(f"⚠️ 긴 문장 많음: {len(long_sentences)}개 (권장: 평균 40-80자)")

        # 3. 불릿 포인트 사용
        bullets = re.findall(r'^[\s]*[-•*]\s+.+$', content, re.MULTILINE)
        if len(bullets) >= 3:
            self.suggestions.append(f"✅ 불릿 포인트: {len(bullets)}개 사용")
        else:
            self.warnings.append(f"⚠️ 불릿 포인트 부족: {len(bullets)}개 (권장: 3개 이상)")

        # 4. 이모지 사용 적절성 (이모지 개수만 간단히 계산)
        emojis = [c for c in content if ord(c) > 0x1F000]  # 이모지는 높은 유니코드 범위
        if 0 < len(emojis) <= 10:
            self.suggestions.append(f"✅ 이모지 사용: {len(emojis)}개 (적절한 수준)")
        elif len(emojis) == 0:
            self.warnings.append(f"⚠️ 이모지 없음 (권장: 2-5개)")
        else:
            self.warnings.append(f"⚠️ 이모지 과다: {len(emojis)}개 (권장: 2-10개)")

        # 5. 표(Table) 사용
        tables = re.findall(r'\|.*\|', content)
        if len(tables) >= 1:
            self.suggestions.append(f"✅ 비교 표: {len(tables)}개 포함")

        # 6. 인용구 사용
        quotes = re.findall(r'> .+', content)
        if len(quotes) >= 1:
            self.suggestions.append(f"✅ 인용구: {len(quotes)}개 포함")

        # 7. 코드/강조 블록
        code_blocks = re.findall(r'`{1,3}[\s\S]*?`{1,3}', content)
        if len(code_blocks) >= 1:
            self.suggestions.append(f"✅ 코드/강조: {len(code_blocks)}개 포함")

        # 8. 헤딩 계층 구조
        h1s = len(re.findall(r'^# ', content, re.MULTILINE))
        h2s = len(re.findall(r'^## ', content, re.MULTILINE))
        if h1s > 1:
            self.warnings.append(f"⚠️ H1 헤딩 과다: {h1s}개 (권장: 1개)")
        if h2s >= 3:
            self.suggestions.append(f"✅ H2 헤딩: {h2s}개 (적절)")

        # 9. 문단 단락 확인
        paragraphs = re.split(r'\n\n+', content)
        if len(paragraphs) >= 10:
            self.suggestions.append(f"✅ 문단 구조: {len(paragraphs)}개 단락 (적절)")
        else:
            self.warnings.append(f"⚠️ 문단 부족: {len(paragraphs)}개 (권장: 10개 이상)")

        # 10. 결론/행동 유도 확인
        if any(word in content.lower() for word in ['결론', '종합', '액션', '투자', '체크리스트', 'cta']):
            self.suggestions.append(f"✅ 명확한 결론/CTA 포함")
        else:
            self.warnings.append(f"⚠️ 명확한 결론 부족")

    def _extract_keywords(self, text: str) -> List[str]:
        """텍스트에서 키워드 추출"""
        # 기본 키워드: 대문자, 숫자 포함 단어
        words = text.split()
        keywords = [w for w in words if (w[0].isupper() or any(c.isdigit() for c in w)) and len(w) > 2]
        return keywords[:5]  # 상위 5개만

    def _calculate_korean_ratio(self, text: str) -> float:
        """한국어 비율 계산"""
        korean_chars = len(re.findall(r'[가-힣]', text))
        total_chars = len(re.sub(r'[\s\n\t]', '', text))
        return (korean_chars / total_chars * 100) if total_chars > 0 else 0

    def _count_sections(self, content: str) -> int:
        """11단계 섹션 개수 계산"""
        section_keywords = [
            r'무슨.*일',
            r'어떻게.*작동',
            r'왜.*영향',
            r'숫자|통계|데이터',
            r'경쟁|비교',
            r'(?:faq|자주)',
            r'전문가|애널리스트',
            r'예측|전망',
            r'결론|종합'
        ]

        found = sum(1 for keyword in section_keywords if re.search(keyword, content, re.IGNORECASE))
        return min(found + 2, 11)  # 최대 11

    def _calculate_score(self) -> int:
        """종합 점수 계산 (0-100)"""
        base_score = 100
        base_score -= len(self.errors) * 20  # 각 오류 -20점
        base_score -= len(self.warnings) * 5  # 각 경고 -5점
        base_score += len(self.suggestions) * 3  # 각 긍정 +3점
        return max(0, min(100, base_score))

    def validate_directory(self, dir_path: str, output_file: str = None) -> Dict:
        """
        디렉토리의 모든 기사 검증

        Args:
            dir_path: 기사 디렉토리 경로
            output_file: 결과 저장 파일 (선택사항)

        Returns:
            검증 결과 종합
        """
        dir_path = Path(dir_path)
        if not dir_path.exists():
            logger.error(f"Directory not found: {dir_path}")
            return {"status": "error", "message": f"디렉토리를 찾을 수 없음: {dir_path}"}

        results = []
        md_files = list(dir_path.glob("*.md"))

        logger.info(f"Validating {len(md_files)} articles in {dir_path}")

        for file_path in md_files:
            result = self.validate_article(str(file_path))
            results.append(result)

        # 종합 통계
        summary = {
            "total_files": len(md_files),
            "validated_files": len(results),
            "average_score": sum(r.get('score', 0) for r in results) / len(results) if results else 0,
            "high_quality": sum(1 for r in results if r.get('score', 0) >= 80),
            "medium_quality": sum(1 for r in results if 60 <= r.get('score', 0) < 80),
            "low_quality": sum(1 for r in results if r.get('score', 0) < 60),
            "results": results
        }

        # 결과 저장
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(summary, f, ensure_ascii=False, indent=2)
                logger.info(f"Validation results saved to {output_file}")
            except Exception as e:
                logger.error(f"Failed to save results: {e}")

        return summary

    def print_report(self, result: Dict, verbose: bool = False):
        """검증 결과 리포트 출력"""
        print("\n" + "=" * 70)
        print(f"📋 기사 품질 검사 결과")
        print("=" * 70)

        print(f"\n📄 파일명: {result.get('file', 'Unknown')}")
        print(f"⏰ 검사 시간: {result.get('timestamp', 'Unknown')}")
        print(f"\n📊 종합 점수: {result.get('score', 0)}/100")
        print(f"✅ 구조 완성도: {result.get('completion_rate', '0%')}")

        # 오류 표시
        if result.get('errors'):
            print(f"\n🔴 오류 ({len(result['errors'])}개):")
            for error in result['errors']:
                print(f"  {error}")

        # 경고 표시
        if result.get('warnings'):
            print(f"\n🟡 경고 ({len(result['warnings'])}개):")
            for warning in result['warnings']:
                print(f"  {warning}")

        # 제안 표시
        if verbose and result.get('suggestions'):
            print(f"\n✅ 긍정 ({len(result['suggestions'])}개):")
            for suggestion in result['suggestions'][:5]:
                print(f"  {suggestion}")
            if len(result['suggestions']) > 5:
                print(f"  ... 외 {len(result['suggestions']) - 5}개")

        print("\n" + "=" * 70)


def main():
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(description="블로그 기사 품질 검사")
    parser.add_argument("--file", help="검사할 기사 파일 경로")
    parser.add_argument("--dir", help="검사할 기사 디렉토리 경로")
    parser.add_argument("--output", help="결과 저장 파일 경로 (JSON)")
    parser.add_argument("--verbose", action="store_true", help="상세 출력")

    args = parser.parse_args()

    validator = ArticleValidator()

    if args.file:
        # 단일 파일 검증
        result = validator.validate_article(args.file)
        validator.print_report(result, verbose=args.verbose)

    elif args.dir:
        # 디렉토리 검증
        summary = validator.validate_directory(args.dir, args.output)
        print("\n" + "=" * 70)
        print("📊 종합 검증 결과")
        print("=" * 70)
        print(f"\n총 파일 수: {summary['total_files']}")
        print(f"평균 점수: {summary['average_score']:.1f}/100")
        print(f"🟢 높음 (80점 이상): {summary['high_quality']}개")
        print(f"🟡 중간 (60-79점): {summary['medium_quality']}개")
        print(f"🔴 낮음 (60점 미만): {summary['low_quality']}개")

        if args.verbose:
            print("\n📋 개별 파일 결과:")
            for result in summary['results']:
                print(f"\n  • {result['file']}: {result['score']}/100 ({result['completion_rate']})")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
