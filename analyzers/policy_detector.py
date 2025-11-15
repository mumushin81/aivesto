"""
정책/규제 변화 감지기
신규 정책, 정책 폐지, 정책 변경 자동 감지
"""
import re
from typing import Dict, List, Optional
from loguru import logger


class PolicyDetector:
    """정부 정책 및 규제 변화 감지"""

    # 정책 변화 키워드
    POLICY_KEYWORDS = {
        'new_policy': [
            # 신규 정책 도입
            'new regulation', 'introduces law', 'passes bill', 'signs executive order',
            'announces policy', 'implements rule', 'enacts legislation',
            'tariff on', 'sanctions against', 'export ban', 'import restriction',
            'tax on', 'subsidy for', 'grant for',

            # 한국어
            '신규 정책', '법안 통과', '행정명령', '규제 도입', '관세 부과',
            '제재 발표', '수출 금지', '세금 부과', '보조금 지급'
        ],

        'policy_removed': [
            # 정책 폐지/완화
            'repeals', 'removes regulation', 'lifts ban', 'ends sanctions',
            'deregulation', 'eases restrictions', 'scraps policy',
            'tariff relief', 'tax cut', 'subsidy cut',

            # 한국어
            '규제 완화', '금지 해제', '제재 해제', '관세 철폐',
            '세금 감면', '보조금 삭감'
        ],

        'policy_changed': [
            # 정책 변경
            'raises interest rate', 'lowers interest rate', 'changes policy',
            'adjusts regulation', 'modifies law', 'amends bill',
            'increases tax', 'reduces tax', 'extends deadline',

            # 한국어
            '금리 인상', '금리 인하', '정책 변경', '세율 조정',
            '법 개정', '기한 연장'
        ]
    }

    # 정부 기관 키워드 (신뢰도 높임)
    GOVERNMENT_AGENCIES = [
        # 미국 연방 기관
        'SEC', 'FTC', 'FDA', 'FCC', 'EPA', 'DOJ', 'Treasury',
        'Federal Reserve', 'Fed', 'White House', 'Congress',
        'Senate', 'House of Representatives',

        # 한국어
        'FDA', '연준', '재무부', '상무부', 'FTC', 'SEC'
    ]

    # 섹터 키워드
    SECTOR_KEYWORDS = {
        'Technology': ['tech', 'software', 'AI', 'chip', 'semiconductor', 'cloud'],
        'Finance': ['bank', 'financial', 'investment', 'trading', 'crypto'],
        'Healthcare': ['pharma', 'biotech', 'drug', 'medical', 'health'],
        'Energy': ['oil', 'gas', 'energy', 'renewable', 'solar', 'wind'],
        'Automotive': ['auto', 'car', 'electric vehicle', 'EV', 'automotive'],
        'Retail': ['retail', 'e-commerce', 'consumer'],
        'Telecom': ['telecom', 'wireless', '5G', 'network']
    }

    def __init__(self):
        logger.info("PolicyDetector initialized")

    def detect(self, text: str) -> Dict:
        """
        정책 변화 감지

        Returns:
            {
                'has_policy_change': True/False,
                'change_type': 'new_policy' | 'policy_removed' | 'policy_changed' | 'none',
                'policy_description': str,
                'affected_sectors': [str],
                'policy_catalyst': str,
                'confidence': float
            }
        """
        text_lower = text.lower()

        # 1. 정책 변화 유형 감지
        change_type = self._detect_change_type(text_lower)

        if change_type == 'none':
            return self._no_policy_result()

        # 2. 정부 기관 언급 확인 (신뢰도 향상)
        has_gov_agency = self._has_government_agency(text)

        # 3. 정책 설명 추출
        policy_description = self._extract_policy_description(text, change_type)

        # 4. 영향 섹터 추출
        affected_sectors = self._extract_affected_sectors(text_lower)

        # 5. 촉매 설명 생성
        policy_catalyst = self._generate_catalyst(change_type, policy_description, affected_sectors)

        # 6. 신뢰도 계산
        confidence = 0.6  # 기본
        if has_gov_agency:
            confidence += 0.3
        if affected_sectors:
            confidence += 0.1

        return {
            'has_policy_change': True,
            'change_type': change_type,
            'policy_description': policy_description,
            'affected_sectors': affected_sectors,
            'policy_catalyst': policy_catalyst,
            'confidence': min(confidence, 1.0)
        }

    def _detect_change_type(self, text_lower: str) -> str:
        """정책 변화 유형 감지"""
        scores = {
            'new_policy': 0,
            'policy_removed': 0,
            'policy_changed': 0
        }

        for change_type, keywords in self.POLICY_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    scores[change_type] += 1

        # 최고 점수 유형 반환
        max_score = max(scores.values())
        if max_score == 0:
            return 'none'

        return max(scores, key=scores.get)

    def _has_government_agency(self, text: str) -> bool:
        """정부 기관 언급 확인"""
        for agency in self.GOVERNMENT_AGENCIES:
            if re.search(r'\b' + re.escape(agency) + r'\b', text, re.IGNORECASE):
                return True
        return False

    def _extract_policy_description(self, text: str, change_type: str) -> str:
        """정책 설명 추출 (첫 문장)"""
        # 정책 키워드가 포함된 문장 찾기
        sentences = text.split('.')

        for sentence in sentences[:5]:  # 첫 5문장만
            sentence_lower = sentence.lower()

            for keyword in self.POLICY_KEYWORDS[change_type]:
                if keyword.lower() in sentence_lower:
                    return sentence.strip()

        return "Policy change detected (details unclear)"

    def _extract_affected_sectors(self, text_lower: str) -> List[str]:
        """영향받는 섹터 추출"""
        sectors = []

        for sector, keywords in self.SECTOR_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    sectors.append(sector)
                    break  # 섹터당 한 번만

        return sectors

    def _generate_catalyst(
        self,
        change_type: str,
        description: str,
        sectors: List[str]
    ) -> str:
        """촉매 설명 생성"""
        if change_type == 'new_policy':
            base = "New regulation may increase costs or restrict operations"
        elif change_type == 'policy_removed':
            base = "Deregulation may boost profitability and market access"
        else:
            base = "Policy change may create winners and losers"

        if sectors:
            sector_str = ', '.join(sectors)
            return f"{base} for {sector_str} sector"

        return base

    def _no_policy_result(self) -> Dict:
        """정책 변화 없음"""
        return {
            'has_policy_change': False,
            'change_type': 'none',
            'policy_description': '',
            'affected_sectors': [],
            'policy_catalyst': '',
            'confidence': 0.0
        }
