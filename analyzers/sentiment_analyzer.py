"""
감성 분석기 - VADER (빠름) + FinBERT (정확) 하이브리드
"""
from typing import Dict, List, Literal
from loguru import logger

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False
    logger.warning("VADER not installed. Install: pip install vaderSentiment")

try:
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("Transformers not installed. Install: pip install transformers torch")


class SentimentAnalyzer:
    """
    감성 분석기 (금융 뉴스 특화)

    - VADER: 빠르지만 덜 정확 (Layer 3용)
    - FinBERT: 느리지만 정확 (Layer 1/2용)
    """

    def __init__(self, use_finbert: bool = False):
        """
        Args:
            use_finbert: FinBERT 사용 여부 (False면 VADER만)
        """
        self.vader = None
        self.finbert_model = None
        self.finbert_tokenizer = None

        # VADER 초기화
        if VADER_AVAILABLE:
            self.vader = SentimentIntensityAnalyzer()
            logger.info("✅ VADER initialized")
        else:
            logger.warning("⚠️  VADER not available")

        # FinBERT 초기화 (선택)
        if use_finbert and TRANSFORMERS_AVAILABLE:
            try:
                model_name = "ProsusAI/finbert"
                self.finbert_tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.finbert_model = AutoModelForSequenceClassification.from_pretrained(model_name)
                self.finbert_model.eval()
                logger.info("✅ FinBERT loaded (금융 뉴스 특화)")
            except Exception as e:
                logger.warning(f"⚠️  FinBERT loading failed: {e}")
                use_finbert = False

        self.use_finbert = use_finbert
        logger.info(f"SentimentAnalyzer ready (FinBERT: {use_finbert})")

    def analyze(
        self,
        text: str,
        method: Literal['vader', 'finbert', 'auto'] = 'auto'
    ) -> Dict[str, any]:
        """
        감성 분석 실행

        Args:
            text: 분석할 텍스트
            method: 'vader', 'finbert', 'auto' (자동 선택)

        Returns:
            {
                'sentiment': 'positive' | 'negative' | 'neutral',
                'score': 0.85,  # -1.0 ~ +1.0
                'confidence': 0.92,
                'method': 'vader' | 'finbert'
            }
        """
        # 자동 선택: 짧은 텍스트는 VADER, 긴 텍스트는 FinBERT
        if method == 'auto':
            if len(text) < 100 or not self.use_finbert:
                method = 'vader'
            else:
                method = 'finbert'

        if method == 'finbert' and self.use_finbert:
            return self._analyze_finbert(text)
        else:
            return self._analyze_vader(text)

    def _analyze_vader(self, text: str) -> Dict:
        """VADER 감성 분석 (빠름)"""
        if not self.vader:
            return self._neutral_result('vader')

        try:
            scores = self.vader.polarity_scores(text)

            # compound: -1 ~ +1
            compound = scores['compound']

            # 레이블 결정
            if compound >= 0.05:
                sentiment = 'positive'
            elif compound <= -0.05:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'

            return {
                'sentiment': sentiment,
                'score': compound,
                'confidence': abs(compound),  # 절대값이 신뢰도
                'method': 'vader',
                'details': scores
            }

        except Exception as e:
            logger.error(f"VADER analysis error: {e}")
            return self._neutral_result('vader')

    def _analyze_finbert(self, text: str) -> Dict:
        """FinBERT 감성 분석 (정확, 금융 특화)"""
        if not self.finbert_model:
            logger.warning("FinBERT not loaded, falling back to VADER")
            return self._analyze_vader(text)

        try:
            # 토큰화 (최대 512 토큰)
            inputs = self.finbert_tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            )

            # 추론
            with torch.no_grad():
                outputs = self.finbert_model(**inputs)
                logits = outputs.logits
                probs = torch.softmax(logits, dim=1).squeeze()

            # FinBERT labels: [negative, neutral, positive]
            negative_prob = probs[0].item()
            neutral_prob = probs[1].item()
            positive_prob = probs[2].item()

            # 가장 높은 확률의 레이블
            max_prob = max(negative_prob, neutral_prob, positive_prob)

            if max_prob == positive_prob:
                sentiment = 'positive'
                score = positive_prob - negative_prob  # -1 ~ +1로 정규화
            elif max_prob == negative_prob:
                sentiment = 'negative'
                score = positive_prob - negative_prob
            else:
                sentiment = 'neutral'
                score = positive_prob - negative_prob

            return {
                'sentiment': sentiment,
                'score': score,
                'confidence': max_prob,
                'method': 'finbert',
                'details': {
                    'positive': positive_prob,
                    'negative': negative_prob,
                    'neutral': neutral_prob
                }
            }

        except Exception as e:
            logger.error(f"FinBERT analysis error: {e}")
            return self._analyze_vader(text)

    def _neutral_result(self, method: str) -> Dict:
        """중립 기본값"""
        return {
            'sentiment': 'neutral',
            'score': 0.0,
            'confidence': 0.0,
            'method': method
        }

    def batch_analyze(self, texts: List[str], method='auto') -> List[Dict]:
        """배치 분석"""
        return [self.analyze(text, method=method) for text in texts]
