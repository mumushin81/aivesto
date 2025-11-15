# Phase 6: 대시보드 실시간 연동 계획

**목표**: 정적 블로그를 Supabase 기반 실시간 뉴스 대시보드로 전환

---

## 📊 현재 상태 분석

### 기존 시스템
- ✅ **데이터 수집**: 417개 기사 자동 수집 (Layer 1 + Layer 2)
- ✅ **분석 엔진**: NER, Sentiment, Policy, Amplification
- ✅ **우선순위 스코어링**: 0-100점 (90+ 정책 시그널)
- ✅ **자동화 스케줄러**: 매 시간 실행
- ✅ **정적 웹**: Flask 기반 마크다운 블로그

### 문제점
- ❌ **실시간성 부족**: 마크다운 파일 기반 (수동 작성)
- ❌ **데이터 단절**: 파이프라인 결과가 대시보드에 반영 안 됨
- ❌ **통계 하드코딩**: "39개 분석된 뉴스" 등이 고정값
- ❌ **필터링 없음**: High-priority 뉴스 구분 안 됨

---

## 🎯 Phase 6 목표

### 1. Supabase 실시간 연동
- 파이프라인이 수집한 기사를 Supabase DB에 자동 저장 (이미 구현됨)
- 대시보드가 Supabase에서 실시간 데이터 가져오기

### 2. 동적 통계 표시
- **실시간 통계**:
  - 총 수집 기사 수
  - High-priority 시그널 (80+점)
  - 정책 시그널 (90+점)
  - 최근 1시간 수집 기사

### 3. 우선순위 필터링
- **필터 옵션**:
  - All / High-Priority (80+) / Policy Signals (90+)
  - 종목별 (AAPL, TSLA, NVDA, etc.)
  - 날짜별

### 4. 자동 새로고침
- 5분마다 자동 새로고침
- 새 기사 도착 시 알림

---

## 🏗️ 구현 계획

### Step 1: Supabase API 엔드포인트 추가 ✅ (이미 구현)

**이미 완료된 기능**:
```python
# database/supabase_client.py
def save_article(self, article: Dict) -> bool:
    # Supabase에 기사 저장
```

**추가 필요**:
```python
def get_recent_articles(self, limit: int = 50, min_priority: int = 0) -> List[Dict]:
    """최근 기사 가져오기 (우선순위 필터링)"""

def get_stats(self) -> Dict:
    """실시간 통계"""
    # total_articles, high_priority_count, policy_signals, last_1h_count

def get_articles_by_symbol(self, symbol: str) -> List[Dict]:
    """종목별 기사 필터링"""
```

### Step 2: Flask API 라우트 추가

```python
# web/app.py

@app.route('/api/stats')
def api_stats():
    """실시간 통계 API"""
    return jsonify(db.get_stats())

@app.route('/api/articles')
def api_articles():
    """기사 목록 API"""
    min_priority = request.args.get('min_priority', 0, type=int)
    symbol = request.args.get('symbol', None)
    limit = request.args.get('limit', 50, type=int)

    if symbol:
        articles = db.get_articles_by_symbol(symbol)
    else:
        articles = db.get_recent_articles(limit, min_priority)

    return jsonify(articles)
```

### Step 3: 대시보드 UI 업데이트

**실시간 통계 섹션**:
```html
<div class="stats" id="live-stats">
    <div class="stat">
        <div class="stat-number" id="total-articles">-</div>
        <div class="stat-label">총 수집 기사</div>
    </div>
    <div class="stat">
        <div class="stat-number" id="high-priority">-</div>
        <div class="stat-label">High-Priority (80+)</div>
    </div>
    <div class="stat">
        <div class="stat-number" id="policy-signals">-</div>
        <div class="stat-label">정책 시그널 (90+)</div>
    </div>
    <div class="stat">
        <div class="stat-number" id="last-hour">-</div>
        <div class="stat-label">최근 1시간</div>
    </div>
</div>
```

**필터 UI**:
```html
<div class="filters">
    <button class="filter-btn active" data-priority="0">All</button>
    <button class="filter-btn" data-priority="80">High-Priority (80+)</button>
    <button class="filter-btn" data-priority="90">Policy Signals (90+)</button>
</div>

<div class="symbol-filters">
    <button class="symbol-btn" data-symbol="">All Symbols</button>
    <button class="symbol-btn" data-symbol="AAPL">AAPL</button>
    <button class="symbol-btn" data-symbol="TSLA">TSLA</button>
    <button class="symbol-btn" data-symbol="NVDA">NVDA</button>
    <!-- ... -->
</div>
```

### Step 4: JavaScript 실시간 업데이트

```javascript
// 초기 로드
async function loadStats() {
    const res = await fetch('/api/stats');
    const stats = await res.json();

    document.getElementById('total-articles').textContent = stats.total_articles;
    document.getElementById('high-priority').textContent = stats.high_priority_count;
    document.getElementById('policy-signals').textContent = stats.policy_signals;
    document.getElementById('last-hour').textContent = stats.last_1h_count;
}

// 기사 로드
async function loadArticles(minPriority = 0, symbol = null) {
    const params = new URLSearchParams({
        min_priority: minPriority,
        limit: 50
    });
    if (symbol) params.append('symbol', symbol);

    const res = await fetch(`/api/articles?${params}`);
    const articles = await res.json();

    renderArticles(articles);
}

// 5분마다 자동 새로고침
setInterval(() => {
    loadStats();
    loadArticles();
}, 5 * 60 * 1000);

// 필터 이벤트
document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        const priority = e.target.dataset.priority;
        loadArticles(priority);
    });
});
```

---

## 📝 데이터 스키마 (Supabase)

### Table: `news_articles`

| Column | Type | Description |
|--------|------|-------------|
| `id` | uuid | Primary key |
| `title` | text | 기사 제목 |
| `url` | text | 원본 URL |
| `source` | text | 출처 (Bloomberg, WSJ, etc.) |
| `symbols` | text[] | 종목 코드 (AAPL, TSLA, etc.) |
| `priority_score` | integer | 우선순위 (0-100) |
| `sentiment` | text | positive/negative/neutral |
| `sentiment_score` | float | -1.0 ~ +1.0 |
| `has_policy_change` | boolean | 정책 변화 여부 |
| `policy_type` | text | new_policy/policy_removed/policy_changed |
| `layer` | integer | 1 (Core) / 2 (Sentiment) |
| `published_at` | timestamp | 발행 시간 |
| `collected_at` | timestamp | 수집 시간 |
| `created_at` | timestamp | DB 저장 시간 |

**Indexes**:
- `idx_priority_score` on `priority_score DESC`
- `idx_collected_at` on `collected_at DESC`
- `idx_symbols` on `symbols` (GIN index)

---

## 🎨 UI 개선 사항

### 우선순위 배지
```html
<div class="article-card" data-priority="{{ article.priority_score }}">
    {% if article.priority_score >= 90 %}
    <span class="badge badge-critical">🔥 정책 시그널</span>
    {% elif article.priority_score >= 80 %}
    <span class="badge badge-high">⚠️ High-Priority</span>
    {% endif %}

    <span class="priority-score">{{ article.priority_score }}점</span>
</div>
```

### 감성 표시
```html
<div class="sentiment {{ article.sentiment }}">
    {% if article.sentiment == 'positive' %}
    📈 긍정적
    {% elif article.sentiment == 'negative' %}
    📉 부정적
    {% else %}
    ⚖️ 중립
    {% endif %}
</div>
```

---

## 🧪 테스트 계획

### 1. API 테스트
```bash
# 통계 확인
curl http://localhost:5001/api/stats

# 기사 목록
curl http://localhost:5001/api/articles?limit=10

# High-priority 필터링
curl http://localhost:5001/api/articles?min_priority=80

# 종목별 필터링
curl http://localhost:5001/api/articles?symbol=AAPL
```

### 2. 실시간 업데이트 테스트
1. 스케줄러 실행 (`python run_scheduler.py`)
2. 1시간 대기 (다음 파이프라인 실행)
3. 대시보드 자동 새로고침 확인

---

## 📊 성공 기준

- ✅ 대시보드가 Supabase에서 실시간 데이터 가져오기
- ✅ 통계가 자동으로 업데이트됨 (하드코딩 제거)
- ✅ High-priority / Policy 필터링 작동
- ✅ 5분마다 자동 새로고침
- ✅ 새 기사가 1시간 내에 대시보드에 반영됨

---

## 🚀 다음 단계 (Phase 7)

- **백테스팅 시스템**: 과거 시그널의 주가 영향 검증
- **알림 시스템**: Telegram/Email 알림
- **모바일 앱**: React Native 또는 Flutter

---

**작성일**: 2025-11-15
**예상 소요 시간**: 4-6시간
