"""
Named Entity Recognition (NER) - 종목 심볼 및 회사명 추출
"""
import re
from typing import List, Dict, Set
from loguru import logger

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    logger.warning("spaCy not installed. Falling back to regex-based extraction.")


class NERExtractor:
    """회사명 및 종목 심볼 추출기"""

    # 주요 종목 심볼 리스트 (확장 가능)
    KNOWN_SYMBOLS = {
        # Tech Giants
        'AAPL': 'Apple', 'MSFT': 'Microsoft', 'GOOGL': 'Google', 'AMZN': 'Amazon',
        'META': 'Meta', 'TSLA': 'Tesla', 'NVDA': 'NVIDIA', 'AMD': 'AMD',
        'INTC': 'Intel', 'NFLX': 'Netflix', 'UBER': 'Uber', 'LYFT': 'Lyft',

        # Finance
        'JPM': 'JPMorgan', 'BAC': 'Bank of America', 'GS': 'Goldman Sachs',
        'MS': 'Morgan Stanley', 'WFC': 'Wells Fargo', 'C': 'Citigroup',

        # Pharma
        'PFE': 'Pfizer', 'JNJ': 'Johnson & Johnson', 'MRNA': 'Moderna',
        'BNTX': 'BioNTech',

        # Retail
        'WMT': 'Walmart', 'TGT': 'Target', 'COST': 'Costco',

        # Energy
        'XOM': 'Exxon Mobil', 'CVX': 'Chevron',

        # Crypto
        'COIN': 'Coinbase', 'MSTR': 'MicroStrategy', 'RIOT': 'Riot Platforms'
    }

    # 역방향 매핑 (회사명 → 심볼)
    COMPANY_TO_SYMBOL = {v.lower(): k for k, v in KNOWN_SYMBOLS.items()}

    def __init__(self, use_spacy: bool = True):
        """
        Args:
            use_spacy: spaCy 사용 여부 (False면 regex만)
        """
        self.use_spacy = use_spacy and SPACY_AVAILABLE
        self.nlp = None

        if self.use_spacy:
            try:
                self.nlp = spacy.load("en_core_web_sm")
                logger.info("✅ spaCy model loaded: en_core_web_sm")
            except Exception as e:
                logger.warning(f"⚠️  Failed to load spaCy model: {e}")
                self.use_spacy = False

        logger.info(f"NERExtractor initialized (spaCy: {self.use_spacy})")

    def extract_symbols(self, text: str) -> List[str]:
        """
        텍스트에서 종목 심볼 추출

        Args:
            text: 뉴스 기사 텍스트

        Returns:
            List of stock symbols (e.g., ['AAPL', 'MSFT'])
        """
        symbols = set()

        # 1. 명시적 심볼 추출 ($AAPL, NASDAQ:AAPL 등)
        symbols.update(self._extract_explicit_symbols(text))

        # 2. 알려진 회사명에서 심볼 매핑
        symbols.update(self._extract_from_company_names(text))

        # 3. spaCy NER (ORG 엔티티)
        if self.use_spacy and self.nlp:
            symbols.update(self._extract_with_spacy(text))

        return sorted(list(symbols))

    def _extract_explicit_symbols(self, text: str) -> Set[str]:
        """명시적 심볼 패턴 추출 ($AAPL, NASDAQ:AAPL)"""
        symbols = set()

        # 패턴 1: $AAPL
        pattern1 = r'\$([A-Z]{1,5})\b'
        matches = re.findall(pattern1, text)
        symbols.update(m for m in matches if m in self.KNOWN_SYMBOLS)

        # 패턴 2: NASDAQ:AAPL, NYSE:TSLA
        pattern2 = r'(?:NASDAQ|NYSE|AMEX):([A-Z]{1,5})\b'
        matches = re.findall(pattern2, text, re.IGNORECASE)
        symbols.update(m.upper() for m in matches if m.upper() in self.KNOWN_SYMBOLS)

        # 패턴 3: (AAPL) 같은 괄호 안 심볼
        pattern3 = r'\(([A-Z]{1,5})\)'
        matches = re.findall(pattern3, text)
        symbols.update(m for m in matches if m in self.KNOWN_SYMBOLS)

        return symbols

    def _extract_from_company_names(self, text: str) -> Set[str]:
        """알려진 회사명에서 심볼 찾기"""
        symbols = set()
        text_lower = text.lower()

        for company, symbol in self.COMPANY_TO_SYMBOL.items():
            # 정확한 단어 매칭 (부분 문자열 방지)
            pattern = r'\b' + re.escape(company) + r'\b'
            if re.search(pattern, text_lower):
                symbols.add(symbol)

        return symbols

    def _extract_with_spacy(self, text: str) -> Set[str]:
        """spaCy NER로 조직명 추출 후 심볼 매핑"""
        symbols = set()

        try:
            doc = self.nlp(text[:5000])  # 첫 5000자만 (속도)

            for ent in doc.ents:
                if ent.label_ == "ORG":  # 조직명
                    org_name = ent.text.lower()

                    # 알려진 회사명과 매칭
                    for company, symbol in self.COMPANY_TO_SYMBOL.items():
                        if company in org_name:
                            symbols.add(symbol)
                            break

        except Exception as e:
            logger.warning(f"spaCy NER error: {e}")

        return symbols

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        전체 엔티티 추출 (심볼, 인물, 조직)

        Returns:
            {
                'symbols': ['AAPL', 'MSFT'],
                'persons': ['Tim Cook', 'Elon Musk'],
                'orgs': ['Apple Inc', 'Tesla']
            }
        """
        result = {
            'symbols': self.extract_symbols(text),
            'persons': [],
            'orgs': []
        }

        if self.use_spacy and self.nlp:
            try:
                doc = self.nlp(text[:5000])

                for ent in doc.ents:
                    if ent.label_ == "PERSON":
                        result['persons'].append(ent.text)
                    elif ent.label_ == "ORG":
                        result['orgs'].append(ent.text)

            except Exception as e:
                logger.warning(f"Entity extraction error: {e}")

        return result

    def add_custom_symbol(self, symbol: str, company_name: str):
        """커스텀 심볼 추가"""
        self.KNOWN_SYMBOLS[symbol] = company_name
        self.COMPANY_TO_SYMBOL[company_name.lower()] = symbol
        logger.info(f"Added custom symbol: {symbol} = {company_name}")
