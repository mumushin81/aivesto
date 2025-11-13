# 📚 API 레퍼런스 (API Reference)

투자 시그널 대시보드의 모든 API 엔드포인트 문서

---

## 🌐 기본 정보

- **Base URL**: `http://localhost:5000`
- **응답 형식**: JSON
- **CORS**: 활성화 (모든 출처 허용)

---

## 📋 API 엔드포인트 목록

### 1. 헬스 체크

#### GET /api/health

서버 상태 확인

**요청**:
```bash
curl http://localhost:5000/api/health
```

**응답** (200 OK):
```json
{
  "status": "healthy",
  "timestamp": "2025-11-13T10:30:45.123456",
  "service": "Investment Signal Dashboard"
}
```

---

## 🔴 긴급 신호 (Level 1)

### GET /api/signals/urgent

즉시 조치가 필요한 신호 조회 (점수 90+)

**쿼리 파라미터**:
| 파라미터 | 타입 | 기본값 | 설명 |
|---------|------|-------|------|
| hours | int | 24 | 최근 N시간 |
| limit | int | 20 | 최대 개수 |

**요청**:
```bash
# 기본 요청
curl http://localhost:5000/api/signals/urgent

# 최근 1시간, 상위 5개
curl "http://localhost:5000/api/signals/urgent?hours=1&limit=5"
```

**응답** (200 OK):
```json
{
  "level": 1,
  "count": 3,
  "signals": [
    {
      "id": "signal-uuid-1",
      "title": "Apple announces record quarterly earnings",
      "url": "https://...",
      "affected_symbols": ["AAPL"],
      "relevance_score": 95,
      "price_impact": "up",
      "importance": "high",
      "signal_level": 1,
      "analysis": {
        "reasoning": "Apple exceeded earnings expectations by 15%, signaling strong demand for iPhones and services",
        "key_points": [
          "Q4 revenue: $123.5B (+10% YoY)",
          "iPhone sales surge 25%",
          "Services revenue hit record high"
        ]
      },
      "created_at": "2025-11-13T10:00:00"
    }
  ]
}
```

---

## 🟠 높은 우선순위 신호 (Level 1-2)

### GET /api/signals/high-priority

높은 우선순위 신호 조회 (점수 80-100)

**쿼리 파라미터**:
| 파라미터 | 타입 | 기본값 | 설명 |
|---------|------|-------|------|
| hours | int | 24 | 최근 N시간 |
| limit | int | 30 | 최대 개수 |

**요청**:
```bash
curl "http://localhost:5000/api/signals/high-priority?hours=6&limit=15"
```

**응답** (200 OK):
```json
{
  "levels": [1, 2],
  "count": 12,
  "signals": [/* Level 1-2 신호들 */]
}
```

---

## 🎯 레벨별 신호 조회

### GET /api/signals/by-level/\<level\>

특정 레벨의 신호 조회

**경로 파라미터**:
| 파라미터 | 타입 | 설명 |
|---------|------|------|
| level | int | 신호 레벨 (1, 2, 3, 4) |

**쿼리 파라미터**:
| 파라미터 | 타입 | 기본값 | 설명 |
|---------|------|-------|------|
| hours | int | 24 | 최근 N시간 |
| limit | int | 50 | 최대 개수 |

**요청**:
```bash
# Level 3 신호 (중간 우선순위)
curl "http://localhost:5000/api/signals/by-level/3?hours=24&limit=20"

# Level 4 신호 (낮음 우선순위)
curl "http://localhost:5000/api/signals/by-level/4?hours=168&limit=100"
```

**응답** (200 OK):
```json
{
  "level": 3,
  "count": 18,
  "signals": [/* 신호 배열 */]
}
```

**신호 레벨 정의**:
| 레벨 | 점수 | 우선순위 | 설명 |
|------|------|---------|------|
| 1 | 90+ | 🔴 긴급 | 즉시 조치 필요 |
| 2 | 80-89 | 🟠 높음 | 고려 필요 |
| 3 | 70-79 | 🟡 중간 | 모니터링 |
| 4 | <70 | 🟢 낮음 | 참고용 |

---

## 📈 종목별 신호 조회

### GET /api/signals/by-symbol/\<symbol\>

특정 종목의 신호 조회

**경로 파라미터**:
| 파라미터 | 타입 | 설명 |
|---------|------|------|
| symbol | str | 종목 심볼 (예: AAPL, MSFT) |

**쿼리 파라미터**:
| 파라미터 | 타입 | 기본값 | 설명 |
|---------|------|-------|------|
| hours | int | 24 | 최근 N시간 |
| limit | int | 20 | 최대 개수 |

**요청**:
```bash
# Microsoft 신호
curl "http://localhost:5000/api/signals/by-symbol/MSFT?hours=24&limit=10"

# Apple 신호 (최근 7일)
curl "http://localhost:5000/api/signals/by-symbol/AAPL?hours=168&limit=20"
```

**응답** (200 OK):
```json
{
  "symbol": "MSFT",
  "count": 5,
  "signals": [
    {
      "title": "Microsoft announces $10B AI investment",
      "affected_symbols": ["MSFT"],
      "relevance_score": 92,
      "signal_level": 1
    }
  ]
}
```

---

## 📊 트렌딩 종목 (신호 기반)

### GET /api/trending-symbols

가장 많은 신호가 나온 종목 조회

**쿼리 파라미터**:
| 파라미터 | 타입 | 기본값 | 설명 |
|---------|------|-------|------|
| hours | int | 24 | 최근 N시간 |
| limit | int | 15 | 최대 개수 |

**요청**:
```bash
# 지난 24시간 트렌딩
curl "http://localhost:5000/api/trending-symbols"

# 지난 7일 상위 20개
curl "http://localhost:5000/api/trending-symbols?hours=168&limit=20"
```

**응답** (200 OK):
```json
{
  "count": 10,
  "symbols": [
    {
      "symbol": "MSFT",
      "count": 12,
      "avg_score": 84.5,
      "urgency_count": 3
    },
    {
      "symbol": "AAPL",
      "count": 10,
      "avg_score": 81.2,
      "urgency_count": 2
    },
    {
      "symbol": "NVDA",
      "count": 8,
      "avg_score": 78.9,
      "urgency_count": 1
    }
  ]
}
```

**응답 필드 설명**:
| 필드 | 설명 |
|------|------|
| symbol | 종목 심볼 |
| count | 신호 개수 |
| avg_score | 평균 관련성 점수 |
| urgency_count | Level 1 (긴급) 신호 개수 |

---

## ⭐ 오늘 주목할 종목

### GET /api/important-symbols

오늘 주목할 종목 (Level 1-2 신호 기반)

**요청**:
```bash
curl http://localhost:5000/api/important-symbols
```

**응답** (200 OK):
```json
{
  "date": "2025-11-13",
  "count": 5,
  "symbols": [
    {
      "symbol": "MSFT",
      "signals": 8,
      "max_score": 92,
      "urgent_count": 2
    },
    {
      "symbol": "AAPL",
      "signals": 6,
      "max_score": 88,
      "urgent_count": 1
    }
  ]
}
```

---

## 📊 대시보드 요약

### GET /api/dashboard

대시보드 전체 요약 (한눈에 보기)

**쿼리 파라미터**:
| 파라미터 | 타입 | 기본값 | 설명 |
|---------|------|-------|------|
| hours | int | 24 | 최근 N시간 |

**요청**:
```bash
# 지난 24시간 요약
curl http://localhost:5000/api/dashboard

# 지난 7일 요약
curl "http://localhost:5000/api/dashboard?hours=168"
```

**응답** (200 OK):
```json
{
  "timestamp": "2025-11-13T10:30:45.123456",
  "period_hours": 24,
  "urgent_count": 3,
  "high_count": 7,
  "medium_count": 12,
  "low_count": 45,
  "trending_symbols": [
    {
      "symbol": "MSFT",
      "count": 12,
      "avg_score": 84.5,
      "urgency_count": 3
    }
  ],
  "latest_signals": [
    {
      "title": "Apple Q4 earnings beat",
      "symbol": "AAPL",
      "score": 95
    }
  ]
}
```

---

## 💰 가격 영향 분석

### GET /api/price-impact

신호의 가격 영향 분석 (상승/하락/중립)

**쿼리 파라미터**:
| 파라미터 | 타입 | 기본값 | 설명 |
|---------|------|-------|------|
| hours | int | 24 | 최근 N시간 |

**요청**:
```bash
curl http://localhost:5000/api/price-impact
```

**응답** (200 OK):
```json
{
  "period_hours": 24,
  "impact": {
    "up": 18,
    "down": 12,
    "neutral": 7
  }
}
```

**해석**:
- `up`: 긍정적 영향 신호 개수
- `down`: 부정적 영향 신호 개수
- `neutral`: 중립적 신호 개수

---

## 📝 글쓰기용 신호 조회

### GET /api/signals-for-article

블로거를 위한 글쓰기 신호 조회

**쿼리 파라미터**:
| 파라미터 | 타입 | 기본값 | 설명 |
|---------|------|-------|------|
| tier | str | tier_1 | 글 등급 (tier_1, tier_2, tier_3) |
| hours | int | 24 | 최근 N시간 |

**요청**:
```bash
# Tier 1 신호 (긴급 + 높음)
curl "http://localhost:5000/api/signals-for-article?tier=tier_1"

# Tier 2 신호 (높음 + 중간)
curl "http://localhost:5000/api/signals-for-article?tier=tier_2&hours=48"

# Tier 3 신호 (모든 신호, 확장된 기간)
curl "http://localhost:5000/api/signals-for-article?tier=tier_3"
```

**응답** (200 OK):
```json
{
  "tier": "tier_1",
  "count": 25,
  "signals": [
    {
      "title": "Breaking: Apple announces AI breakthrough",
      "affected_symbols": ["AAPL"],
      "relevance_score": 94,
      "signal_level": 1,
      "analysis": {
        "key_points": [
          "New AI chip 50% faster",
          "Energy consumption reduced by 30%",
          "Available in next generation products"
        ]
      }
    }
  ]
}
```

---

## 🔔 신호 처리 표시

### POST /api/signal/\<signal_id\>/process

신호를 처리된 것으로 표시 (향후 기능)

**경로 파라미터**:
| 파라미터 | 타입 | 설명 |
|---------|------|------|
| signal_id | str | 신호 UUID |

**요청**:
```bash
curl -X POST http://localhost:5000/api/signal/550e8400-e29b-41d4-a716-446655440000/process
```

**응답** (200 OK):
```json
{
  "signal_id": "550e8400-e29b-41d4-a716-446655440000",
  "processed": true
}
```

---

## ❌ 에러 응답

### 404 Not Found

```json
{
  "error": "Not Found"
}
```

### 400 Bad Request

```json
{
  "error": "Invalid level. Must be 1-4"
}
```

### 500 Internal Server Error

```json
{
  "error": "Internal Server Error"
}
```

---

## 🔗 사용 예시

### Python

```python
import requests

BASE_URL = "http://localhost:5000/api"

# 긴급 신호 조회
response = requests.get(f"{BASE_URL}/signals/urgent?limit=5")
signals = response.json()

for signal in signals['signals']:
    print(f"🔴 {signal['title']}")
    print(f"   점수: {signal['relevance_score']}/100")
    print(f"   종목: {', '.join(signal['affected_symbols'])}")

# 트렌딩 종목
response = requests.get(f"{BASE_URL}/trending-symbols?limit=10")
trending = response.json()

for i, symbol in enumerate(trending['symbols'], 1):
    print(f"{i}. {symbol['symbol']}: {symbol['count']} signals")
```

### JavaScript (Fetch)

```javascript
const API_BASE = "http://localhost:5000/api";

async function getUrgentSignals() {
  const response = await fetch(`${API_BASE}/signals/urgent?limit=5`);
  const data = await response.json();

  data.signals.forEach(signal => {
    console.log(`🔴 ${signal.title}`);
    console.log(`   Score: ${signal.relevance_score}/100`);
    console.log(`   Symbols: ${signal.affected_symbols.join(", ")}`);
  });
}

getUrgentSignals();
```

### CURL

```bash
# 모든 쿼리 파라미터 포함
curl -s "http://localhost:5000/api/signals/urgent?hours=24&limit=10" \
  -H "Content-Type: application/json" | jq '.'

# 결과를 파일로 저장
curl "http://localhost:5000/api/dashboard" > dashboard.json

# 특정 필드만 추출
curl -s "http://localhost:5000/api/trending-symbols" | \
  jq '.symbols[].symbol'
```

---

## 📊 응답 시간

| 엔드포인트 | 응답 시간 | 참고 |
|-----------|---------|-----|
| /api/health | <10ms | 캐시됨 |
| /api/signals/* | 50-200ms | 데이터베이스 쿼리 |
| /api/dashboard | 100-300ms | 집계 연산 |
| /api/trending-symbols | 200-500ms | 복잡한 계산 |

---

## 🔐 레이트 제한

현재 레이트 제한 없음 (개발 환경)

프로덕션에서는 다음을 권장:
- 사용자당 100 요청/분
- IP당 1000 요청/분

---

## 📚 참고

- [Flask API 문서](https://flask.palletsprojects.com)
- [JSON 형식 가이드](https://www.json.org)
- [HTTP 상태 코드](https://httpwg.org/specs/rfc9110.html)

---

**마지막 업데이트**: 2025-11-13
**API 버전**: 1.0.0
